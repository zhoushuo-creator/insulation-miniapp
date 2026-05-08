"""
RAG 对话服务 — 向量检索增强生成
流程: 用户问题 → 向量检索(pgvector) → 构造提示词 → DeepSeek生成
"""
import json
import httpx
from typing import List, Optional, Dict, Any
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductVariant
from app.models.embedding import ProductEmbedding, DocumentChunk
from app.models.chat import ChatSession, ChatMessage
from app.services.embedding import create_query_embedding
from app.core.config import settings


def _build_product_context(products: List[Product]) -> str:
    """Build text context from a list of products for the LLM prompt."""
    parts = []
    for p in products:
        info = {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "model": p.model,
            "description": p.description,
            "specs": p.specs,
            "reference_price": p.reference_price,
            "unit": p.unit,
        }
        parts.append(json.dumps(info, ensure_ascii=False, default=str))
    return "\n".join(parts)


async def _semantic_search(db: AsyncSession, embedding: List[float], top_k: int = 5) -> List[Product]:
    """Search products by vector similarity using pgvector cosine distance."""
    from sqlalchemy.orm import selectinload

    if not embedding:
        return []

    embedding_str = ",".join(str(x) for x in embedding)
    # Use pgvector's cosine distance: <=> operator
    # Subquery: get min distance per product (dedup), then join + sort
    query = text(f"""
        SELECT p.*, best.distance
        FROM (
            SELECT pe.product_id, MIN(pe.embedding <=> '[{embedding_str}]'::vector) AS distance
            FROM product_embeddings pe
            GROUP BY pe.product_id
        ) best
        JOIN products p ON p.id = best.product_id
        WHERE p.is_published = true
        ORDER BY best.distance ASC
        LIMIT :limit
    """).bindparams(limit=top_k)

    try:
        result = await db.execute(query)
        rows = result.fetchall()
    except Exception as e:
        print(f"Semantic search error: {e}")
        return []

    if not rows:
        return []

    # Sort by distance for final result
    rows.sort(key=lambda r: r[-1])
    product_ids = [row[0] for row in rows]
    stmt = (
        select(Product)
        .options(selectinload(Product.variants), selectinload(Product.scenarios))
        .where(Product.id.in_(product_ids))
    )
    result = await db.execute(stmt)
    products = {p.id: p for p in result.unique().scalars().all()}
    # Preserve similarity order
    return [products[pid] for pid in product_ids if pid in products]


async def rag_chat(
    db: AsyncSession,
    user_message: str,
    session_id: Optional[int] = None,
    openid: Optional[str] = None,
) -> Dict[str, Any]:
    """
    RAG-enhanced chat:
    1. Get or create chat session
    2. Save user message
    3. Embed query
    4. Semantic search products
    5. Construct prompt
    6. Call DeepSeek
    7. Save assistant message
    8. Return response + sources
    """
    # 1. Session
    if session_id:
        result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = result.scalar_one_or_none()
    if not session_id or not session:
        session = ChatSession(openid=openid)
        db.add(session)
        await db.flush()

    # 2. Save user message
    user_msg = ChatMessage(session_id=session.id, role="user", content=user_message)
    db.add(user_msg)
    await db.flush()

    # 3. Embed query
    query_embedding = await create_query_embedding(user_message)

    # 4. Semantic search
    matched_products = await _semantic_search(db, query_embedding, top_k=settings.RAG_TOP_K)

    # 5. Build prompt
    product_context = _build_product_context(matched_products) if matched_products else "暂无匹配产品"

    system_prompt = """你是保温材料领域的专业顾问。请根据数据库中的产品信息回答用户问题。

规则:
1. 基于提供的产品数据给出专业建议
2. 如产品库无匹配，诚实告知并给出通用选材建议
3. 回答包含具体产品名称、品牌、规格参数和参考价格
4. 语气专业、简洁
5. 用中文回答"""

    user_prompt = f"""数据库匹配到的相关产品:
{product_context}

用户问题: {user_message}

请根据以上产品信息回答用户问题。"""

    # 6. Call DeepSeek
    sources = []
    assistant_content = ""
    llm_model = ""

    if matched_products:
        sources = [
            {"id": p.id, "name": p.name, "brand": p.brand, "reference_price": p.reference_price}
            for p in matched_products
        ]

    if settings.DEEPSEEK_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{settings.DEEPSEEK_API_BASE}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.DEEPSEEK_CHAT_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1000,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                assistant_content = data["choices"][0]["message"]["content"]
                llm_model = data.get("model", settings.DEEPSEEK_CHAT_MODEL)
        except Exception as e:
            assistant_content = f"抱歉，AI 服务暂时不可用。请根据以下产品信息自行参考选用。错误: {e}"
            llm_model = "fallback"
    else:
        assistant_content = "AI 服务未配置 API Key。请在管理后台设置 DeepSeek API Key 后重试。"
        llm_model = "unconfigured"

    # 7. Save assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=assistant_content,
        sources=sources,
        llm_model=llm_model,
    )
    db.add(assistant_msg)
    await db.flush()

    # 8. Update session title (first message)
    if not session.title:
        session.title = user_message[:40]
        if len(user_message) > 40:
            session.title += "..."

    return {
        "session_id": session.id,
        "message": {
            "id": assistant_msg.id,
            "role": "assistant",
            "content": assistant_content,
            "sources": sources,
            "llm_model": llm_model,
        },
    }


async def smart_recommend(
    db: AsyncSession,
    requirements: str,
) -> Dict[str, Any]:
    """
    Smart product recommendation: embed requirements → search → recommend.
    Returns matched products with explanation.
    """
    # Embed query
    query_embedding = await create_query_embedding(requirements)

    # Search
    matched = await _semantic_search(db, query_embedding, top_k=settings.RAG_TOP_K)

    products_out = []
    for p in matched:
        products_out.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "model": p.model,
            "description": p.description,
            "reference_price": p.reference_price,
            "unit": p.unit,
            "specs": p.specs,
            "cover_image": p.cover_image,
            "variants": [
                {
                    "id": v.id,
                    "name": v.name,
                    "thickness": v.thickness,
                    "density": v.density,
                    "price": v.price,
                }
                for v in (p.variants or [])
            ],
        })

    return {
        "requirements": requirements,
        "products": products_out,
    }


async def list_sessions(db: AsyncSession, openid: Optional[str] = None) -> List[Dict[str, Any]]:
    """List chat sessions, optionally filtered by user."""
    query = select(ChatSession).order_by(ChatSession.updated_at.desc()).limit(50)
    if openid:
        query = query.where(ChatSession.openid == openid)
    result = await db.execute(query)
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "title": s.title or "新对话",
            "openid": s.openid,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in sessions
    ]


async def get_session_detail(db: AsyncSession, session_id: int) -> Optional[Dict[str, Any]]:
    """Get session with its messages."""
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        return None

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()

    return {
        "id": session.id,
        "title": session.title,
        "openid": session.openid,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "sources": m.sources,
                "llm_model": m.llm_model,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }
