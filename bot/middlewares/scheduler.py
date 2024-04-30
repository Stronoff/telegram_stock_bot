from __future__ import annotations
from typing import TYPE_CHECKING, Any
from aiogram import BaseMiddleware
from bot.core.loader import scheduler

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import Update


class SchedulerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        data["scheduler"] = scheduler
        return await handler(event, data)
