"""模型配置相关 VO。"""

from datetime import datetime

from app.schemas.base import ORMBase


class ModelVO(ORMBase):
    """用户自己的模型连接配置，API KEY 只返回掩码。"""

    id: str
    display_name: str
    provider: str
    model_name: str
    base_url: str | None = None
    context_window: int
    max_output_tokens: int
    masked_key: str
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ModelTestVO(ORMBase):
    """模型连接测试结果。"""

    success: bool
    latency_ms: int
    message: str
