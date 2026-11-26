"""业务异常。"""


class AppError(Exception):
    """业务错误，统一由全局处理器转成 Result。"""

    def __init__(self, code: int, message: str, status_code: int = 200):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)
