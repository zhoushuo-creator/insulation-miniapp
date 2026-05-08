"""
AI 对话 & 智能推荐端点 (RAG 方案)
流程: 用户消息 → 向量嵌入 → pgvector相似度搜索 → 构建Prompt → LLM生成 → 返回
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.deps import get_current_user
from app.services.embedding_pipeline import generate_product_embeddings
from app.core.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    openid: Optional[str] = None


class RecommendRequest(BaseModel):
    requirements: str


@router.post("/chat")
async def ai_chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """AI 智能顾问对话（RAG 增强）"""
    from app.services.rag import rag_chat
    result = await rag_chat(
        db,
        user_message=req.message,
        session_id=req.session_id,
        openid=req.openid,
    )
    return result


@router.post("/chat/stream")
async def ai_chat_stream(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """AI 对话流式输出 (SSE)"""
    from app.services.rag import rag_chat
    import json

    async def event_stream():
        try:
            result = await rag_chat(
                db,
                user_message=req.message,
                session_id=req.session_id,
                openid=req.openid,
            )
            # For now, send as single event; can be enhanced to true streaming
            content = result["message"]["content"]
            # Simulate streaming by chunking
            chunk_size = 20
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield f"data: {json.dumps({'chunk': chunk, 'done': False}, ensure_ascii=False)}\n\n"
            # Send sources as final event
            yield f"data: {json.dumps({'chunk': '', 'done': True, 'sources': result['message']['sources'], 'session_id': result['session_id']}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/recommend")
async def smart_recommend(
    req: RecommendRequest,
    db: AsyncSession = Depends(get_db),
):
    """智能推荐：根据需求推荐合适产品"""
    from app.services.rag import smart_recommend as do_recommend
    result = await do_recommend(db, req.requirements)
    return result


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    openid: Optional[str] = None,
):
    """用户的历史对话列表"""
    from app.services.rag import list_sessions as do_list
    items = await do_list(db, openid=openid)
    return {"items": items}


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取对话会话详情（含所有消息）"""
    from app.services.rag import get_session_detail
    detail = await get_session_detail(db, session_id)
    if not detail:
        raise HTTPException(status_code=404, detail="会话不存在")
    return detail


@router.post("/generate-embeddings")
async def generate_embeddings(
    product_ids: Optional[list[int]] = None,
    db: AsyncSession = Depends(get_db),
):
    """为产品生成向量嵌入（管理端调用）"""
    count = await generate_product_embeddings(db, product_ids)
    return {"message": f"已为 {count} 个产品生成向量嵌入"}
