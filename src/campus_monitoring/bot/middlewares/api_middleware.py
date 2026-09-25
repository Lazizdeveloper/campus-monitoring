from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from campus_monitoring.api.client import School21ApiClient


class ApiClientMiddleware(BaseMiddleware):
    def __init__(self, api_client: School21ApiClient):
        super().__init__()
        self.api_client = api_client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["api_client"] = self.api_client
        return await handler(event, data)
