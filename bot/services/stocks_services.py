from datetime import datetime, timedelta
from typing import List

import loguru
from tinkoff.invest import AsyncClient, GetLastTradesResponse, ShareResponse, GetTradingStatusResponse
from tinkoff.invest.grpc.instruments_pb2 import INSTRUMENT_ID_TYPE_TICKER

from bot.core.config import TZ


async def get_share_diff(token: str, ticker: str | List, interval: int) -> tuple[float, int]:
    end: datetime = datetime.now(TZ)
    start = end - timedelta(seconds=interval)

    if interval > 60 * 60:
        return None, None

    if start + timedelta(seconds=interval//5) < datetime(end.year, end.month, end.day, 7, tzinfo=TZ):
        return 0, 0
    elif end + timedelta(seconds=interval//5) > datetime(end.year, end.month, end.day, 20, 50, tzinfo=TZ):
        return 0, 0

    async with AsyncClient(token) as client:
        instrument: ShareResponse = await client.instruments.share_by(id_type=INSTRUMENT_ID_TYPE_TICKER,
                                                                      class_code='TQBR', id=ticker)
        trades: GetLastTradesResponse = await client.market_data \
            .get_last_trades(instrument_id=instrument.instrument.uid, from_=start, to=end)

        first_trades = [x for x in trades.trades if x.time < start + timedelta(seconds=interval // 5)]
        last_trades = [x for x in trades.trades if x.time > end - timedelta(seconds=interval // 5)]
        if len(first_trades) == 0 or len(last_trades) == 0:
            return -2, -2
        start_price = sum([x.price.units + x.price.nano / 1_000_000_000 for x in first_trades]) / len(first_trades)
        last_price = sum([x.price.units + x.price.nano / 1_000_000_000 for x in last_trades]) / len(last_trades)

        return round((last_price - start_price) / start_price * 100, 2), len(trades.trades)
