"""认证端点 — 微信小程序登录 + 管理后台扫码登录"""
import uuid
import time
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter()

# In-memory admin QR login state (dev only; use Redis in production)
_qrcode_store: dict[str, dict] = {}


class WxLoginRequest(BaseModel):
    code: str
    nickname: str | None = None
    avatar_url: str | None = None


class AdminScanRequest(BaseModel):
    token: str
    openid: str


@router.post("/wx-login")
async def wx_login(req: WxLoginRequest, db: AsyncSession = Depends(get_db)):
    """小程序微信登录 — code 换取 JWT Token"""
    # 1. Exchange code for openid (dev mode: skip if no real appid)
    openid = None
    is_dev_appid = not settings.WX_APPID or settings.WX_APPID.startswith("wx-your")
    if (settings.WX_APPID and settings.WX_SECRET and not is_dev_appid):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.weixin.qq.com/sns/jscode2session",
                    params={
                        "appid": settings.WX_APPID,
                        "secret": settings.WX_SECRET,
                        "js_code": req.code,
                        "grant_type": "authorization_code",
                    },
                )
                data = resp.json()
                openid = data.get("openid")
        except Exception:
            pass  # API call failed, fall through to dev mode

    # Dev fallback for all cases where WeChat API didn't return openid
    if not openid:
        openid = req.code or f"dev-{uuid.uuid4().hex[:12]}"

    # 2. Find or create user
    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            openid=openid,
            nickname=req.nickname or f"用户{openid[:8]}",
            avatar_url=req.avatar_url,
        )
        db.add(user)
        await db.flush()
    else:
        if req.nickname:
            user.nickname = req.nickname
        if req.avatar_url:
            user.avatar_url = req.avatar_url
        await db.flush()

    # 3. Generate JWT
    token = create_access_token({"sub": str(user.id), "openid": openid})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "openid": user.openid,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
            "is_admin": user.is_admin,
        },
    }


@router.get("/admin/qrcode")
async def admin_login_qrcode():
    """管理后台扫码登录 — 生成临时 token"""
    token = uuid.uuid4().hex
    _qrcode_store[token] = {"status": "pending", "openid": None, "created_at": time.time()}
    # Clean expired tokens (older than 5 minutes)
    now = time.time()
    expired = [k for k, v in _qrcode_store.items() if now - v["created_at"] > 300]
    for k in expired:
        del _qrcode_store[k]
    # In production, return QR image URL; dev: return token for console use
    return {"token": token, "expires_in": 300}


@router.get("/admin/qrcode/status")
async def admin_qrcode_status(token: str):
    """轮询扫码状态"""
    entry = _qrcode_store.get(token)
    if not entry:
        return {"status": "expired"}
    if entry["status"] == "confirmed":
        # Clean up and return JWT
        openid = entry["openid"]
        del _qrcode_store[token]
        return {"status": "confirmed", "openid": openid}
    return {"status": "pending"}


@router.get("/admin/qrcode/confirm")
async def admin_qrcode_confirm(token: str, openid: str):
    """管理后台扫码成功后获取 JWT（前端轮询到 confirmed 后调用）"""
    result = await db_verify_admin(openid)
    if not result:
        raise HTTPException(status_code=403, detail="非管理员账号")
    token_jwt = create_access_token({"sub": openid, "admin": True})
    return {"token": token_jwt, "openid": openid}


@router.post("/admin/scan")
async def admin_scan_confirm(req: AdminScanRequest, db: AsyncSession = Depends(get_db)):
    """小程序端扫码确认登录"""
    # Verify admin
    is_admin = req.openid in settings.ADMIN_WECHAT_IDS
    if not is_admin:
        # Also check DB
        result = await db.execute(select(User).where(User.openid == req.openid))
        user = result.scalar_one_or_none()
        is_admin = user is not None and user.is_admin

    entry = _qrcode_store.get(req.token)
    if not entry:
        raise HTTPException(status_code=400, detail="二维码已过期")

    if is_admin:
        entry["status"] = "confirmed"
        entry["openid"] = req.openid
        return {"message": "确认成功"}
    else:
        return {"message": "非管理员账号，无法登录后台"}


async def db_verify_admin(openid: str) -> bool:
    """Helper: check if openid belongs to an admin."""
    if openid in settings.ADMIN_WECHAT_IDS:
        return True
    return False
