"""
RAG 检索服务 — ChromaDB 知识库检索与构建
"""

import os

from config.settings import settings


# 懒加载 ChromaDB collection
_collection = None
_client = None


def _get_collection():
    """获取或创建 ChromaDB collection（懒加载）"""
    global _collection, _client
    if _collection is None:
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            persist_dir = settings.CHROMA_PERSIST_DIR
            os.makedirs(persist_dir, exist_ok=True)

            _client = chromadb.PersistentClient(
                path=persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            _collection = _client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            _collection = False  # 标记为不可用
    return _collection


def ping_chromadb() -> tuple:
    """检测 ChromaDB 是否连通"""
    try:
        col = _get_collection()
        if col is False:
            return False, "初始化失败"
        col.count()
        return True, "connected"
    except Exception as e:
        return False, str(e)


def search_knowledge(query: str, top_k: int = None) -> list:
    """
    检索与 query 最相关的心理学知识。

    返回:
        [{"title": "...", "content": "...", "score": 0.92}, ...]
    """
    if top_k is None:
        top_k = settings.RAG_TOP_K

    col = _get_collection()
    if col is False or col is None:
        return []

    try:
        # 用 sentence-transformers 做 embedding
        from ml_models.emotion import get_embedding_model
        embedding_model = get_embedding_model()

        if embedding_model is None:
            return []

        query_vec = embedding_model.encode(query).tolist()
        results = col.query(
            query_embeddings=[query_vec],
            n_results=top_k,
        )

        if not results or not results.get("documents") or not results["documents"][0]:
            return []

        output = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results.get("metadatas", [[{}]])[0]
            distances = results.get("distances", [[0]])[0]
            score = round(1 - distances[i], 4) if i < len(distances) else 0
            output.append({
                "title": meta[i].get("title", "") if i < len(meta) else "",
                "content": doc,
                "score": score,
            })
        return output

    except Exception:
        return []


def build_knowledge_base(kb_dir: str = None, rebuild: bool = False):
    """
    从 knowledge base 目录构建 ChromaDB 向量索引。
    供 backend/scripts/build_kb.py 调用。

    参数:
        kb_dir:  txt 文件所在目录，默认 data/psychology_kb/
        rebuild: 是否清空重来
    """
    import glob

    if kb_dir is None:
        kb_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "psychology_kb")
    kb_dir = os.path.abspath(kb_dir)

    if not os.path.isdir(kb_dir):
        print(f"[build_kb] 目录不存在: {kb_dir}")
        return

    col = _get_collection()
    if col is False:
        print("[build_kb] ChromaDB 不可用，跳过构建")
        return

    if rebuild:
        try:
            _client.delete_collection(settings.CHROMA_COLLECTION)
            global _collection
            _collection = _client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            pass

    txt_files = glob.glob(os.path.join(kb_dir, "*.txt"))
    if not txt_files:
        print(f"[build_kb] 没有找到 .txt 文件在 {kb_dir}")
        return

    from ml_models.emotion import get_embedding_model
    embedding_model = get_embedding_model()
    if embedding_model is None:
        print("[build_kb] Embedding 模型不可用")
        return

    new_count = 0
    for filepath in txt_files:
        title, keywords, content = _parse_kb_file(filepath)
        if not content.strip():
            continue

        # 按段落切割
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 30]
        if not paragraphs:
            paragraphs = [content.strip()]

        embeddings = embedding_model.encode(paragraphs).tolist()
        ids = [f"{os.path.basename(filepath)}_p{i}" for i in range(len(paragraphs))]
        metadatas = [{"title": title, "keywords": keywords, "source": os.path.basename(filepath)} for _ in paragraphs]

        try:
            col.add(
                ids=ids,
                documents=paragraphs,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            new_count += len(paragraphs)
            print(f"[build_kb] 已导入: {os.path.basename(filepath)} → {len(paragraphs)} chunks")
        except Exception as e:
            print(f"[build_kb] 导入失败 {os.path.basename(filepath)}: {e}")

    print(f"[build_kb] 完成，共新增 {new_count} 条")


def _parse_kb_file(filepath: str) -> tuple:
    """
    解析知识库 txt 文件，提取元数据。

    格式约定:
    ---
    title: 焦虑症的非药物干预
    keywords: 焦虑, CBT, 正念
    ---
    正文...
    """
    title = os.path.basename(filepath).replace(".txt", "")
    keywords = ""
    content_start = 0
    lines = []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if line == "---":
                content_start = i + 1
                break
            if line.startswith("title:"):
                title = line.replace("title:", "").strip()
            elif line.startswith("keywords:"):
                keywords = line.replace("keywords:", "").strip()

    content = "".join(lines[content_start:]) if content_start > 0 else "".join(lines)
    return title, keywords, content
