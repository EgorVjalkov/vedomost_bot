from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class SetTimebyHandMiddleWare(BaseMiddleware):
    def __init__(self, category_name):
        self.name = category_name

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        print(self.name)
        if self.name:
            if 'sleeptime' in self.name:
                return await handler(event, data)
