"""ORM 实体统一出口。

新增模型后记得在这里导入，否则建表脚本看不到。
"""

from app.models.base import Base
from app.models.user import User

__all__ = ["Base", "User"]
