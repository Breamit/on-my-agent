"""用户接口。"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import Result
from app.db.session import get_db
from app.schemas import UserCreateDTO, UserVO
from app.services import user_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/user/create", summary="创建用户")
async def create_user(
    dto: UserCreateDTO,
    db: AsyncSession = Depends(get_db),
) -> Result[UserVO]:
    # 只记录定位问题的字段，不要打印整个 DTO（里面有密码）
    logger.info("创建用户 username=%s nickname=%s", dto.username, dto.nickname)
    return Result.ok(await user_service.create_user(db, dto))
