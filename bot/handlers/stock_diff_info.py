from aiogram import Router, types, F, Bot
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

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


async def send_share_diff(bot: Bot, user_id, token, ticker, interval, limit):
    delta, cnt = await get_share_diff(token, ticker, interval)
    if cnt == -2:
        await bot.send_message(user_id, f"{delta}; {cnt}")

    logger.info(f"Sending share_diff to user {user_id}, {delta}, {cnt}")
    if abs(delta) >= limit:
        await bot.send_message(
            user_id,
            f"{ticker} изменился на {delta}% за последние {round(300 / 60, 2)} минут.\n"
            f"Количество сделок: {cnt}")
