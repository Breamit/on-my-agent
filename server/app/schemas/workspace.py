"""工作区文件相关 VO。"""

from datetime import datetime

from app.schemas.base import ORMBase


class WorkspaceFileVO(ORMBase):
    """工作区文件元数据，来源于文件系统。"""

    file_id: str
    name: str
    path: str
    size: int
    mime_type: str
    updated_at: datetime
