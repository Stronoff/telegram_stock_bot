from aiogram import Router, types, F, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.stock_diff_info import send_share_diff
from bot.core.loader import bot
from bot.services.users import get_user_token
from bot.services.scheduled_jobs import add_job


router = Router(name="scheduler_manager")


@router.message(F.text.startswith("/get_schedules"))
async def get_schedules(message: types.Message, scheduler: AsyncIOScheduler):
    jobs = [' '.join(x.name.split('_')[1:]) for x in scheduler.get_jobs()]
    logger.info(f'{jobs}')
    text = "\n".join(jobs) if len(jobs) > 0 else "No jobs registered"
    await message.answer(f"{text}")


@router.message(F.text.startswith("/delete_schedule"))
async def delete_schedule(message: types.Message, scheduler: AsyncIOScheduler):
    info = message.text.split(' ')[1:]
    info.insert(0, str(message.from_user.id))
    job_name = '_'.join(info)
    jobs_to_remove = [x for x in scheduler.get_jobs() if x.name == job_name]
    [job.remove() for job in jobs_to_remove]
    await message.answer(f"Scheduled job {job_name.split('_')[1:]} deleted.")


@router.message(F.text.startswith("/register_scheduler"))
async def register_scheduler_handler(message: types.Message, session: AsyncSession,
                                     scheduler: AsyncIOScheduler) -> None:
    logger.info("Registering new scheduler")
    if len(message.text.split(' ')) < 4:
        await message.answer("Нехватает аргументов.\nИспользование: "
                             "/register_scheduler <Тикер> <Частота проверки> <Лимит для срабатывания> <Кол-во сделок>")
        return

    token = await get_user_token(session, message.from_user.id)
    _, ticker, interval, limit = message.text.split(' ')
    user_id = int(message.from_user.id)
    job = scheduler.add_job(send_share_diff, 'interval', seconds=int(interval),
                            kwargs={
                                'user_id': user_id,
                                'ticker': ticker,
                                'token': token,
                                'interval': int(interval),
                                'limit': int(limit)
                            },
                            name=f'{user_id}_{ticker}_{interval}_{limit}')


    # await add_job(session, message.from_user.id, job.id)
