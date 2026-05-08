from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """统一参数校验错误返回格式"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field, "message": error["msg"]})
    return JSONResponse(
        status_code=422,
        content={"detail": "参数校验失败", "errors": errors},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"},
    )


def not_found(message: str = "资源不存在") -> HTTPException:
    return HTTPException(status_code=404, detail=message)


def forbidden(message: str = "无权限访问") -> HTTPException:
    return HTTPException(status_code=403, detail=message)


def bad_request(message: str = "请求参数有误") -> HTTPException:
    return HTTPException(status_code=400, detail=message)


def unauthorized(message: str = "请先登录") -> HTTPException:
    return HTTPException(status_code=401, detail=message)
