"""用户相关的 DTO / VO。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.base import ORMBase


class UserVO(ORMBase):
    """用户信息。"""

    id: str
    username: str
    nickname: str
    created_at: datetime


class TokenVO(ORMBase):
    """登录成功后返回的令牌。"""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserVO


class UserCreateDTO(BaseModel):
    """创建用户的请求体。"""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[A-Za-z0-9_]+$",
        description="登录账号，3-64 位字母、数字、下划线",
        examples=["alice"],
    )
    password: str = Field(
        min_length=6,
        max_length=128,
        description="登录密码，6-128 位",
        examples=["secret123"],
    )
    nickname: str = Field(
        default="",
        max_length=64,
        description="显示昵称，为空时使用 username",
    )

    @field_validator("username", "nickname", mode="before")
    @classmethod
    def strip_text(cls, value):
        """先去掉首尾空格，再做长度和格式校验。"""
        return value.strip() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def password_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("密码不能为空白")
        # bcrypt 最多处理 72 字节，中文等多字节字符按 UTF-8 计算
        if len(value.encode("utf-8")) > 72:
            raise ValueError("密码不能超过 72 字节")
        return value

    @model_validator(mode="after")
    def fill_nickname(self) -> "UserCreateDTO":
        """昵称不传时使用 username。"""
        if not self.nickname:
            self.nickname = self.username
        return self
