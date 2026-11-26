"""v1 版本路由聚合（对应 SpringBoot 的 @RequestMapping("/api/v1")）。

新模块在这里 include_router 注册即可，main.py 不用改。
"""

from fastapi import APIRouter

from app.api.v1 import test , user

api_router = APIRouter()
api_router.include_router(test.router, tags=["test"])
api_router.include_router(user.router, tags=["user"])
