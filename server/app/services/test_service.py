"""测试模块的业务逻辑（对应 SpringBoot 的 @Service）。"""

from app.schemas.test import HelloData


def get_hello() -> HelloData:
    return HelloData(message="Hello World")
