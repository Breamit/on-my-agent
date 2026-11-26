"""初始化数据库表。

运行：
    cd server
    .venv/Scripts/python.exe -m scripts.init_db
"""

import asyncio

import app.models  # noqa: F401  注册所有模型到 Base.metadata
from app.db.session import engine
from app.models.base import Base


async def init() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("建表完成")


if __name__ == "__main__":
    asyncio.run(init())
