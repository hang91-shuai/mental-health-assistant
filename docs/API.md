# API 接口文档

**Base URL**: `http://localhost:5000`

所有接口统一返回格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

错误时 `code != 200`：

```json
{
  "code": 400,
  "message": "缺少 text 字段",
  "data": null
}
```

---

## 1. GET /api/ping

连通性测试。

**返回**:

```json
{
  "code": 200,
  "data": { "status": "ok", "message": "server running" }
}
```

---

## 2. GET /api/health

健康检查，诊断所有依赖服务状态。

**返回**:

```json
{
  "code": 200,
  "data": {
    "healthy": true,
    "components": {
      "bert_model": "loaded",
      "ollama": "connected",
      "chromadb": "connected",
      "session_count": 12
    }
  }
}
```

---

## 3. POST /api/analyze

情绪分析。

**请求**:

```json
{
  "text": "我最近总是很焦虑，睡不着觉"
}
```

**返回**:

```json
{
  "code": 200,
  "data": {
    "emotion": "焦虑",
    "label": "anxiety",
    "score": 0.87,
    "confidence": 0.87,
    "top3": [
      { "label": "焦虑", "score": 0.87 },
      { "label": "悲伤", "score": 0.06 },
      { "label": "恐惧", "score": 0.03 }
    ]
  }
}
```

**约束**:
- `text` 必填，1~500 字

---

## 4. POST /api/chat

对话接口（一次请求完成 情绪分析 + RAG + 千问回复）。

**请求**:

```json
{
  "message": "我好焦虑，有什么办法缓解吗",
  "session_id": "uuid-from-previous-chat"
}
```

- `session_id` 可选，首次不传会自动创建
- `message` 必填，1~1000 字

**返回**:

```json
{
  "code": 200,
  "data": {
    "reply": "我理解你现在感觉很焦虑...(千问回复)",
    "emotion": {
      "emotion": "焦虑",
      "label": "anxiety",
      "score": 0.87,
      "confidence": 0.87,
      "top3": [...]
    },
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "knowledge_refs": ["焦虑症的非药物干预"]
  }
}
```

---

## 错误码速查

| code | 含义 |
|------|------|
| 200  | 成功 |
| 400  | 请求参数错误 |
| 404  | 资源未找到 |
| 500  | 服务器内部错误 |
