import datetime
import time
from datetime import datetime, timedelta
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
                if tag in settings.INSTRUMENTS_TAGS_MAPPING:
                    tag = settings.INSTRUMENTS_TAGS_MAPPING[tag]

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
                now = datetime.now(TZ)
                market_data = [
                    await client.market_data.get_last_trades(instrument_id=a.uid, from_=now - timedelta(minutes=5), to=now + timedelta(minutes=1))
                    for a in instruments_list]
                market_data: List[List[Trade]] = [x.trades for x in market_data]
                if len(market_data) > 0:
                    prices_prev_min = [[x.price.units + x.price.nano / 1_000_000_000 for x in trades if
                                        now - timedelta(minutes=1) < x.time < now - timedelta(seconds=30)]
                                       for trades in market_data]
                    prices_now = [[x.price.units + x.price.nano / 1_000_000_000 for x in trade if
                                   now - timedelta(seconds=30) <= x.time]
                                  for trade in market_data]
                    delta = []
                    loguru.logger.info(f"previous prices: {prices_prev_min}; current prices: {prices_now}")
                    for price_prev, price_now in zip(prices_prev_min, prices_now):
                        if price_prev and price_now:
                            avg_prev = sum(price_prev) / len(price_prev)
                            avg_new = sum(price_now) / len(price_now)
                            delta.append(round((avg_new - avg_prev) / avg_prev * 100, 2))
                        else:
                            delta.append(0)
                else:
                    delta = [0] * len(instruments_list)
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
                                       reply_markup=buy_sell_kb(instruments_list, delta))
