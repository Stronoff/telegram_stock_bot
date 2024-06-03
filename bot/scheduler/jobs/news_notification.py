import datetime
from datetime import datetime, timedelta
import time
from typing import List

import loguru
from aiogram import Bot
from tinkoff.invest import AsyncClient
from tinkoff.invest.grpc.common_pb2 import INSTRUMENT_TYPE_SHARE
from tinkoff.invest.grpc.instruments_pb2 import FindInstrumentResponse, InstrumentShort
from tinkoff.invest.schemas import Trade

from bot.core.config import settings, TZ
from bot.keyboards.inline.stocks import buy_sell_kb
from bot.services.news_parser import get_last_news


async def send_news(bot: Bot, user_id: int, token: int):
    s = time.time()
    loguru.logger.info("Start parsing news")
    news = await get_last_news(settings.NEWS_LINK, settings.MAX_RESULTS_NEWS, settings.DATA_FILE_NEWS)

    if news is None:
        return
    loguru.logger.info(f"Got {len(news)} new news")
    for x in news:
        if x['title'] is None:
            await bot.send_message(user_id, f"Error parsing page {x['link']}")
            return
        async with AsyncClient(token=token) as client:
            instruments_list: List[InstrumentShort] = []
            for tag in x['tags']:
                loguru.logger.info(f"Searching tag {tag}")
                instruments: FindInstrumentResponse = await client.instruments.find_instrument(query=tag,
                                                                                               api_trade_available_flag=True,
                                                                                               instrument_kind=INSTRUMENT_TYPE_SHARE)
                instruments_list += instruments.instruments

            if len(instruments_list) == 0:
                e = time.time()
                await bot.send_message(user_id,
                                       f"Failed to find ticker from tags:\n"
                                       f"Tags: {x['tags']};\n"
                                       f"Title: {x['title']}\n"
                                       f"Content: {' '.join(x['content'])}\n"
                                       f"Link: {x['link']}\n"
                                       f"ML Score: In work :(\n"
                                       f"Time elapsed: {e - s}")
            else:
                ticker_str = " #".join([x.ticker for x in instruments_list])
                name_str = " #".join([x.name for x in instruments_list])
                market_data: List[List[Trade]] = [x.trades for x in
                                                  await client.market_data.get_last_trades(instrument_id=a.uid)
                                                  for a in instruments_list]
                now = datetime.now(TZ)
                prices_prev_min = [[x.price for x in trade] for trade in market_data if
                                   now - timedelta(minutes=1) < x.time < now - timedelta(seconds=30)]
                prices_now = [[x.price for x in trade ]for trade in market_data if
                              now - timedelta(seconds=30) <= x.time]
                avg_prev = [sum(x)/len(x) for x in prices_prev_min]
                avg_new = [sum(x)/len(x) for x in prices_now]
                delta = [round((b-a)/b*100, 2) for a, b in zip(avg_prev, avg_new)]
                e = time.time()
                await bot.send_message(user_id,
                                       f"#{ticker_str} \n"
                                       f"#{name_str} \n"
                                       f"Price change: {delta}\n"
                                       f"Tags: {x['tags']};\n"
                                       f"Title: {x['title']}\n"
                                       f"Content: {' '.join(x['content'])}\n"
                                       f"Link: {x['link']}\n"
                                       f"ML Score: In work :(\n"
                                       f"Time elapsed: {e - s}",
                                       reply_markup=buy_sell_kb(instruments_list))
