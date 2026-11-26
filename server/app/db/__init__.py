"""数据访问层。

统一导出数据库引擎、会话工厂和 FastAPI 依赖。
"""

from app.db.session import SessionLocal, engine, get_db

__all__ = ["SessionLocal", "engine", "get_db"]
