"""文件上传端点 — 产品图片 + 纸质资料"""
import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.config import settings

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_CATALOG_TYPES = {"image/jpeg", "image/png", "application/pdf", "image/tiff"}
MAX_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def _ensure_upload_dir(subdir: str) -> str:
    path = os.path.join(settings.UPLOAD_DIR, subdir)
    os.makedirs(path, exist_ok=True)
    return path


@router.post("/product-image")
async def upload_product_image(file: UploadFile = File(...)):
    """上传产品图片"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, f"不支持的图片格式: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, f"文件超过 {settings.MAX_UPLOAD_SIZE_MB}MB 限制")

    ext = os.path.splitext(file.filename or "image.png")[1] or ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(_ensure_upload_dir("products"), filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return {"url": f"/uploads/products/{filename}", "filename": filename}


@router.post("/catalog")
async def upload_catalog(file: UploadFile = File(...)):
    """上传纸质资料图片/PDF"""
    if file.content_type not in ALLOWED_CATALOG_TYPES:
        raise HTTPException(400, f"不支持的文件格式: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, f"文件超过 {settings.MAX_UPLOAD_SIZE_MB}MB 限制")

    ext = os.path.splitext(file.filename or "catalog.pdf")[1] or ".pdf"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(_ensure_upload_dir("catalogs"), filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return {
        "id": filename.replace(ext, ""),
        "filename": file.filename,
        "saved_as": filename,
        "size": len(content),
        "status": "uploaded",
    }


@router.get("/catalogs")
async def list_catalogs():
    """已上传的资料列表"""
    catalog_dir = os.path.join(settings.UPLOAD_DIR, "catalogs")
    items = []
    if os.path.exists(catalog_dir):
        for f in sorted(os.listdir(catalog_dir), reverse=True):
            fpath = os.path.join(catalog_dir, f)
            items.append({
                "id": os.path.splitext(f)[0],
                "filename": f,
                "size": os.path.getsize(fpath),
                "status": "uploaded",
            })
    return {"items": items}


@router.post("/catalogs/{catalog_id}/process")
async def process_catalog(catalog_id: str):
    """触发资料数字化流程：OCR → 分块 → 嵌入向量"""
    # Phase 5+: Full OCR pipeline (Tesseract/paddleocr → chunk → embed)
    return {"message": "OCR 处理已加入队列", "catalog_id": catalog_id, "status": "queued"}
