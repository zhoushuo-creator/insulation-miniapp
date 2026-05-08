"""
向量嵌入服务 — 通义千问 DashScope text-embedding-v3
"""
import httpx
from typing import List, Optional
from app.core.config import settings


async def create_embeddings(texts: List[str]) -> Optional[List[List[float]]]:
    """
    Generate 1024-dimension embeddings via DashScope.
    Returns a list of embeddings, one per input text.
    """
    if not settings.DASHSCOPE_API_KEY:
        return None

    url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # DashScope supports batch input
            payload = {
                "model": settings.DASHSCOPE_EMBED_MODEL,
                "input": {"texts": texts},
                "parameters": {"text_type": "document"},
            }
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # Response: {"output": {"embeddings": [{"text_index": 0, "embedding": [...]}]}}
            embeddings_raw = data.get("output", {}).get("embeddings", [])
            # Sort by text_index to maintain order
            embeddings_raw.sort(key=lambda x: x.get("text_index", 0))
            return [e["embedding"] for e in embeddings_raw]
    except Exception as e:
        print(f"Embedding API error: {e}")
        return None


async def create_query_embedding(text: str) -> Optional[List[float]]:
    """
    Generate a single embedding for a search query.
    Uses query-specific text_type for better retrieval.
    """
    if not settings.DASHSCOPE_API_KEY:
        return None

    url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": settings.DASHSCOPE_EMBED_MODEL,
                "input": {"texts": [text]},
                "parameters": {"text_type": "query"},
            }
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            embeddings = data.get("output", {}).get("embeddings", [])
            if embeddings:
                return embeddings[0].get("embedding")
            return None
    except Exception as e:
        print(f"Query embedding error: {e}")
        return None
