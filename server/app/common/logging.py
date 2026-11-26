"""统一日志配置。

特性：
- 控制台 + 按大小滚动的文件日志，默认写入 server/logs/app.log
- 时间统一使用 UTC
- 每次请求分配 request_id，并回写到响应头 X-Request-ID
- 对 api_key、password、token 等敏感字段做脱敏

使用方式：
    from app.common.logging import setup_logging
    setup_logging()

业务模块直接使用标准库：
    logger = logging.getLogger(__name__)
"""

import logging
import logging.handlers
import re
import sys
import time
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from app.common.config import BASE_DIR, settings

# 当前请求 ID，由 main.py 的中间件写入
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

# 敏感字段名（整键匹配，避免误伤 token_used 这类普通字段）
_SENSITIVE_KEY = re.compile(
    r"(?i)^(api[_-]?key|authorization|password|passwd|secret|access[_-]?token|refresh[_-]?token)$"
)

# 形如 api_key=xxx、password: xxx 的片段
_SENSITIVE_INLINE = re.compile(
    r"(?i)\b(api[_-]?key|authorization|password|passwd|secret|access[_-]?token|refresh[_-]?token)\b"
    r"(\s*[=:]\s*)"
    r"([^\s,;\"'}\]]+)"
)


def mask_secret(value: str, keep: int = 4) -> str:
    """把密钥类字符串替换成可辨认的掩码，例如 sk-1***abcd。"""
    if not value:
        return "***"
    if len(value) <= keep * 2:
        return "***"
    return f"{value[:keep]}***{value[-keep:]}"


def mask_sensitive(text: str) -> str:
    """对日志文本里形如 key=value 的敏感片段做脱敏。"""
    return _SENSITIVE_INLINE.sub(lambda m: f"{m.group(1)}{m.group(2)}***", text)


def _mask_args(args: Any) -> Any:
    """递归处理日志参数，字典中敏感键的值直接替换为掩码。"""
    if isinstance(args, dict):
        return {
            key: ("***" if _SENSITIVE_KEY.match(str(key)) else _mask_args(value))
            for key, value in args.items()
        }
    if isinstance(args, tuple):
        return tuple(_mask_args(item) for item in args)
    if isinstance(args, list):
        return [_mask_args(item) for item in args]
    if isinstance(args, str):
        return mask_sensitive(args)
    return args


class _RequestIdFilter(logging.Filter):
    """把当前请求 ID 注入日志记录。"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


class _SensitiveFilter(logging.Filter):
    """过滤日志中的密码、API KEY 等敏感内容。"""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = mask_sensitive(record.msg)
        if record.args:
            record.args = _mask_args(record.args)
        return True


class _UTCFormatter(logging.Formatter):
    """使用 UTC 时间格式化日志。"""

    converter = time.gmtime


def setup_logging() -> None:
    """初始化日志。重复调用会替换本模块创建的 handler，不影响外部 handler。"""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    log_dir = Path(settings.log_dir)
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    # Windows 控制台默认可能是 GBK，中文日志会乱码
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    formatter = _UTCFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(level)

    # 只清理本模块之前创建过的 handler，避免影响测试或 uvicorn 的 handler
    for handler in root.handlers[:]:
        if getattr(handler, "_oma_handler", False):
            root.removeHandler(handler)
            handler.close()

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.addFilter(_RequestIdFilter())
    console.addFilter(_SensitiveFilter())
    console._oma_handler = True  # type: ignore[attr-defined]
    root.addHandler(console)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(_RequestIdFilter())
    file_handler.addFilter(_SensitiveFilter())
    file_handler._oma_handler = True  # type: ignore[attr-defined]
    root.addHandler(file_handler)

    # 降低第三方库噪音；请求访问日志由 main.py 的中间件统一输出
    for name in (
        "uvicorn.access",
        "sqlalchemy.engine",
        "httpx",
        "httpx2",
        "httpx_sse",
        "httpcore",
        "watchfiles",
        "watchfiles.main",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)
