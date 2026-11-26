"""会话相关 VO。"""

from datetime import datetime

from app.schemas.base import ORMBase


class SessionVO(ORMBase):
    """会话信息。"""

    id: str
    title: str
    model_config_id: str | None = None
    system_prompt: int
    input_token_used: int
    output_token_used: int
    is_pinned: bool
    sort_order: int
    last_conversation_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class SessionTitleVO(ORMBase):
    """会话标题。"""

    id: str
    title: str
