"""统一响应体（对应 SpringBoot 里的 Result<T> / 全局返回包装）。

所有接口统一返回：{ "code": 0, "message": "success", "data": ... }
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: T | None = None

    @classmethod
    def ok(cls, data: T | None = None, message: str = "success") -> "Result[T]":
        return cls(code=0, message=message, data=data)

    @classmethod
    def fail(cls, code: int, message: str) -> "Result[T]":
        return cls(code=code, message=message, data=None)


class PageVO(BaseModel, Generic[T]):
    """分页响应体。"""

    total: int
    page: int
    page_size: int
    items: list[T]
