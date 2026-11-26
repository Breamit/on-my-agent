"""用户业务逻辑。"""

import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import AppError
from app.models.user import User
from app.schemas import UserCreateDTO, UserVO


def hash_password(password: str) -> str:
    """用 bcrypt 生成密码哈希。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """校验明文密码和哈希是否匹配。"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


async def create_user(db: AsyncSession, dto: UserCreateDTO) -> UserVO:
    """创建用户：查重、哈希密码、入库。"""
    exists = await db.scalar(select(User.id).where(User.username == dto.username))
    if exists:
        raise AppError(2002, "用户名已存在")

    user = User(
        username=dto.username,
        nickname=dto.nickname or dto.username,
        password=hash_password(dto.password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        # 并发情况下唯一索引兜底
        await db.rollback()
        raise AppError(2002, "用户名已存在") from None

    await db.refresh(user)
    return UserVO.model_validate(user)
