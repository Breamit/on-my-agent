"""启动入口

运行：
    python main.py
或：
    uvicorn main:app --reload
"""

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.common.config import settings
from app.common.errors import AppError
from app.common.logging import request_id_ctx, setup_logging
from app.common.response import Result

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    # 前后端分离：允许前端跨域访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """记录参数校验失败详情，并返回统一的 Result 结构。"""
        errors = exc.errors()
        logger.warning(
            "参数校验失败 %s %s: %s",
            request.method,
            request.url.path,
            errors,
        )
        first = errors[0] if errors else {}
        location = ".".join(str(part) for part in first.get("loc", [])[1:]) or "body"
        message = first.get("msg", "参数错误")
        return JSONResponse(
            status_code=422,
            content=Result.fail(1001, f"{location}: {message}").model_dump(),
        )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """业务异常统一返回 Result。"""
        logger.warning(
            "业务异常 %s %s: code=%s message=%s",
            request.method,
            request.url.path,
            exc.code,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=Result.fail(exc.code, exc.message).model_dump(),
        )

    @app.middleware("http")
    async def request_log_middleware(request: Request, call_next):
        """为每个请求分配 request_id，并记录访问日志。"""
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        token = request_id_ctx.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("请求异常 %s %s", request.method, request.url.path)
            raise
        else:
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "%s %s -> %d %.1fms",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)

    # 所有 v1 接口统一挂在 /api/v1 下
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    logger.info(
        "应用启动：%s v%s（debug=%s）",
        settings.app_name,
        settings.app_version,
        settings.debug,
    )
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # 使用 app.common.logging 的统一配置
        # 日志文件写在 server/logs 下，不排除会被 --reload 当成代码变更
        reload_excludes=[
            "logs/*",
            "*.log",
            "__pycache__/*",
            "*.pyc",
            ".venv/*",
        ],
    )
