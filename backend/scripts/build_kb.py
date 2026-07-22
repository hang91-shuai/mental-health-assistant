"""
知识库构建脚本 — 从 data/psychology_kb/ 构建 ChromaDB 向量索引

用法:
    cd backend
    python scripts/build_kb.py              # 增量更新
    python scripts/build_kb.py --rebuild     # 清空重建
"""

import os
import sys
import argparse

# 把 backend/ 加入 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main():
    parser = argparse.ArgumentParser(description="构建心理学知识库向量索引")
    parser.add_argument("--rebuild", action="store_true", help="清空已有数据重新构建")
    parser.add_argument("--dir", type=str, default=None, help="知识库 txt 目录路径")
    args = parser.parse_args()

    from services.rag_service import build_knowledge_base

    print("=" * 50)
    print("开始构建知识库索引...")
    print(f" rebuild = {args.rebuild}")
    print("=" * 50)

    build_knowledge_base(kb_dir=args.dir, rebuild=args.rebuild)

    print("完成。")


if __name__ == "__main__":
    main()
