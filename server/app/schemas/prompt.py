"""系统提示词相关 VO。"""

from datetime import datetime

from app.schemas.base import ORMBase


class PromptVO(ORMBase):
    """系统提示词。"""

    id: int
    name: str
    prompt: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
