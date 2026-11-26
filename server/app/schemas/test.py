"""测试模块的数据模型（对应 SpringBoot 的 DTO / VO）。"""

from pydantic import BaseModel


class HelloData(BaseModel):
    message: str
