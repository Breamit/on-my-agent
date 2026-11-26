"""测试接口（对应 SpringBoot 的 @RestController）。

Router 只负责接收请求、调用 Service、返回结果，业务逻辑不写在这里。
"""

from fastapi import APIRouter

from app.common.response import Result
from app.schemas.test import HelloData
from app.services import test_service

router = APIRouter()


@router.get("/test", response_model=Result[HelloData], summary="连通性测试")
def test() -> Result[HelloData]:
    return Result.ok(test_service.get_hello())
