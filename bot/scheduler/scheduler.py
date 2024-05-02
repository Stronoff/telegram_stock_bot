import loguru
from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.events import JobExecutionEvent
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler_di import ContextSchedulerDecorator
from rodi import Container
from loguru import logger
from tzlocal import get_localzone

from bot.core.config import Settings
from bot.database.database import sessionmaker
from bot.scheduler.exceptions import DeleteRequest


async def handle_job_error(event: JobExecutionEvent, ctx: Container):
    logger.error(f'{event.exception=}')
    if isinstance(event.exception, DeleteRequest):
        scheduler = ctx.build_provider().get(BaseScheduler)
        scheduler.remove_job(event.job_id)


def setup_scheduler(bot: Bot = None, settings: Settings = None, storage: RedisStorage = None, session_pool=None):
    job_stores = {
        "default": RedisJobStore(
            db=2,
            host=settings.REDIS_HOST,
            password=settings.REDIS_PASS,
            port=settings.REDIS_PORT,
            jobs_key="dispatched_trips_jobs",
            run_times_key="dispatched_trips_running"
        )
    }

    scheduler = ContextSchedulerDecorator(
        AsyncIOScheduler(jobstores=job_stores, timezone=str(get_localzone()))
    )
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(scheduler, declared_class=BaseScheduler)
    scheduler.ctx.add_instance(storage, declared_class=RedisStorage)
    scheduler.ctx.add_instance(session_pool, declared_class=sessionmaker)

    scheduler.on_job_error += handle_job_error
    return scheduler
