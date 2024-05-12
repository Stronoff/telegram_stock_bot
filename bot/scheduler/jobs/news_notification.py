from aiogram import Bot
from loguru import logger

from bot.services.news_parser import get_last_news
from bot.core.config import settings


async def send_news(bot: Bot, user_id: int):
    news = await get_last_news(settings.NEWS_LINK, settings.MAX_RESULTS_NEWS, settings.DATA_FILE_NEWS)
    logger.info(f"Get news data for {news}")
    if news is None:
        return

    for x in news:
        await bot.send_message(user_id, f"{x['tags']}\n{x['title']}\n{x['content']}")
