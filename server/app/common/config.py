"""应用配置

所有配置项都来自环境变量或 server/.env，代码里不提供默认值。
配置优先级：环境变量 > .env 文件。
缺少必填项时启动直接失败，避免带着错误配置运行。
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# server/ 目录，.env 就放在这里
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",  # 环境变量统一加 APP_ 前缀，如 APP_PORT=8000
        extra="ignore",
    )

    # 应用
    app_name: str = Field(..., description="应用名称")
    app_version: str = Field(..., description="应用版本")
    debug: bool = Field(..., description="是否开启调试和热重载")
    host: str = Field(..., description="监听地址")
    port: int = Field(..., ge=1, le=65535, description="监听端口")
    api_v1_prefix: str = Field(..., description="API 路径前缀")

    # 跨域
    cors_origins: list[str] = Field(..., description="允许跨域的前端地址")

    # 日志
    log_level: str = Field(..., description="日志级别")
    log_dir: str = Field(..., description="日志目录，相对路径以 server/ 为基准")
    log_max_bytes: int = Field(..., gt=0, description="单个日志文件大小上限")
    log_backup_count: int = Field(..., ge=0, description="日志保留份数")

    # 数据库
    database_url: str = Field(..., description="MySQL 异步连接串")

    # JWT
    jwt_secret: str = Field(..., description="JWT 签名密钥")
    jwt_expire_minutes: int = Field(..., gt=0, description="JWT 有效期，单位分钟")

    # API KEY 加密
    aes_key: str = Field(..., description="AES-256-GCM 密钥，Base64 编码的 32 字节")

    # 管理员
    admin_usernames: list[str] = Field(..., description="管理员用户名列表")

    # 工作区与技能
    workspace_root: str = Field(..., description="用户工作区根目录")
    skill_root: str = Field(..., description="技能目录")

    # 运行限制
    max_upload_size: int = Field(..., gt=0, description="单文件上传大小上限，单位字节")
    llm_timeout: int = Field(..., gt=0, description="模型请求超时，单位秒")
    skill_timeout: int = Field(..., gt=0, description="技能执行超时，单位秒")
    agent_max_turns: int = Field(..., ge=1, le=50, description="Agent 最大循环轮数")


# 全局唯一配置对象，其他模块直接 from app.common.config import settings
settings = Settings()
