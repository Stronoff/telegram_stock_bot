from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.core.loader import i18n as _i18n


def register_middlewares(dp: Dispatcher, scheduler: AsyncIOScheduler) -> None:
    from .auth import AuthMiddleware
    from .database import DatabaseMiddleware
    from .i18n import ACLMiddleware
    from .logging import LoggingMiddleware
    from .throttling import ThrottlingMiddleware
    from .scheduler import SchedulerMiddleware

    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(LoggingMiddleware())

    dp.update.outer_middleware(DatabaseMiddleware())

    dp.update.outer_middleware(SchedulerMiddleware(scheduler))

    dp.message.middleware(AuthMiddleware())

    dp.message.middleware(ACLMiddleware(i18n=_i18n))
    dp.callback_query.middleware(ACLMiddleware(i18n=_i18n))
    dp.inline_query.middleware(ACLMiddleware(i18n=_i18n))

    dp.callback_query.middleware(CallbackAnswerMiddleware())