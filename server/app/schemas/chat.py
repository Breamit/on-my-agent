"""对话消息相关 VO。"""

from datetime import datetime
from typing import Literal

from app.schemas.base import ORMBase


class MessageVO(ORMBase):
    """一条对话消息。"""

    id: str
    session_id: str
    parent_id: str | None = None
    seq: int
    model_config_id: str | None = None
    model_name: str | None = None
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    reasoning_content: str | None = None
    input_token: int
    output_token: int
    msg_status: int
    error_message: str | None = None
    created_at: datetime
