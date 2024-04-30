from aiogram import Router, types, F, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.loader import bot
from bot.services.stocks_services import get_share_diff
from bot.services.users import get_user_token

router = Router(name="share_diff")


@router.message(F.text.startswith("/get_diff"))
async def share_diff_handler(message: types.Message, session: AsyncSession) -> None:
    _, ticker, interval = message.text.split(' ')
    token = await get_user_token(session, message.from_user.id)
    logger.info(f"{ticker},{interval}")

    delta, cnt = await get_share_diff(token, ticker, int(interval))
    if delta is None and cnt is None:
        await message.answer("Интервал должен быть меньше часа или мало сделок за это интервал")
    await message.answer(f"{ticker} изменился на {delta}% за последние {round(int(interval) / 60, 2)} минут.\n"
                         f"Количество сделок: {cnt}")


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

    job = scheduler.add_job(send_share_diff, 'interval', seconds=int(interval),
                            args=[bot, message.from_user.id, token, ticker, int(interval), float(limit)])


async def send_share_diff(bot: Bot, user_id, token, ticker, interval, limit):
    delta, cnt = await get_share_diff(token, ticker, interval)
    if cnt == -2:
        await bot.send_message("")

    logger.info(f"Sending share_diff to user {user_id}, {delta}, {cnt}")
    if abs(delta) >= limit:
        await bot.send_message(
            user_id,
            f"{ticker} изменился на {delta}% за последние {round(300 / 60, 2)} минут.\n"
            f"Количество сделок: {cnt}")
