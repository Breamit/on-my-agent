"""Schema 基类。

所有 VO 继承该类，开启从 SQLAlchemy 模型直接转换的能力。
"""

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """支持从 ORM 对象构造的基类。"""

    model_config = ConfigDict(from_attributes=True)
