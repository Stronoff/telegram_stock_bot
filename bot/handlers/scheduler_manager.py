from aiogram import Router, types, F
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.stock_diff_info import send_share_diff
from bot.scheduler.jobs.news_notification import send_news
from bot.services.users import get_user_token

router = Router(name="scheduler_manager")


@router.message(F.text.startswith("/get_schedules"))
async def get_schedules(message: types.Message, scheduler: AsyncIOScheduler):
    jobs = [job.id for job in scheduler.get_jobs()]
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
    _ = scheduler.add_job(send_share_diff, 'interval', seconds=int(interval),
                          kwargs={
                              'user_id': user_id,
                              'ticker': ticker,
                              'token': token,
                              'interval': int(interval),
                              'limit': int(limit)
                          },
                          name=f'{user_id}_{ticker}_{interval}_{limit}')


@router.message(F.text.startswith("/news_scheduler"))
async def news_scheduler_handler(message: types.Message, scheduler: AsyncIOScheduler, session: AsyncSession) -> None:
    user_id = message.from_user.id

    if scheduler.get_job(f'news_scheduler_{user_id}'):
        logger.info(f"{scheduler.get_job(f'news_scheduler_{user_id}')}")
        await message.answer("Scheduler already running! If you want to stop run /stop_news")
        return

    token = await get_user_token(session, message.from_user.id)
    scheduler.add_job(send_news,
                      trigger='interval',
                      seconds=10,
                      id=f'news_scheduler_{user_id}',
                      kwargs={'user_id': user_id,
                              'token': token})
    await message.answer("New news scheduled successfully added!")


@router.message(F.text.startswith("/stop_news"))
async def news_scheduler_remove(message: types.Message, scheduler: AsyncIOScheduler) -> None:
    if scheduler.get_job(f'news_scheduler_{message.from_user.id}'):
        scheduler.remove_job(f'news_scheduler_{message.from_user.id}')
        await message.answer("News scheduler removed")
    else:
        await message.answer("News scheduler not registered! If you want to create run `/news_scheduler`")
