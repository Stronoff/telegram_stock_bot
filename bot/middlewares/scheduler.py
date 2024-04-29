from __future__ import annotations
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import Update


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: AsyncIOScheduler) -> None:
        self._scheduler = scheduler
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        data["scheduler"] = self._scheduler
