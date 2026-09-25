class School21ApiError(Exception):
    """Base exception for School 21 API errors."""
    def __init__(self, message: str, status_code: int = 500, code: str = "ERROR", uuid: str = ""):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.uuid = uuid

    def __str__(self) -> str:
        return f"[{self.status_code} {self.code}] {self.message}"


class UnauthorizedError(School21ApiError):
    """Raised when API token is invalid or missing (401)."""
    def __init__(self, message: str = "Avtorizatsiya xatosi. Token noto'g'ri yoki muddati tugagan.", uuid: str = ""):
        super().__init__(message=message, status_code=401, code="UNAUTHORIZED", uuid=uuid)


class ForbiddenError(School21ApiError):
    """Raised when access is forbidden (403)."""
    def __init__(self, message: str = "Ruxsat etilmagan amal (403 Forbidden).", uuid: str = ""):
        super().__init__(message=message, status_code=403, code="FORBIDDEN", uuid=uuid)


class NotFoundError(School21ApiError):
    """Raised when resource/participant is not found (404)."""
    def __init__(self, message: str = "Ma'lumot topilmadi (404 Not Found).", uuid: str = ""):
        super().__init__(message=message, status_code=404, code="NOT_FOUND", uuid=uuid)


class RateLimitError(School21ApiError):
    """Raised when rate limit is exceeded (429)."""
    def __init__(self, message: str = "So'rovlar soni me'yoridan oshib ketdi (429 Too Many Requests).", uuid: str = ""):
        super().__init__(message=message, status_code=429, code="TOO_MANY_REQUESTS", uuid=uuid)


class ServerError(School21ApiError):
    """Raised when server returns an internal error (500)."""
    def __init__(self, message: str = "Server ichki xatoligi (500 Internal Server Error).", uuid: str = ""):
        super().__init__(message=message, status_code=500, code="INTERNAL_SERVER_ERROR", uuid=uuid)
