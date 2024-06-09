import decimal
from typing import List

import loguru
from tinkoff.invest import AsyncClient
from tinkoff.invest.grpc.instruments_pb2 import INSTRUMENT_ID_TYPE_UID
from tinkoff.invest.schemas import OrderType, OrderDirection, Order
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal

from bot.core.config import settings


async def post_order(token: int, account_id: int, uid: str, bid: int, direction: str) -> (decimal.Decimal, int):
    async with AsyncClient(token) as client:
        r = await client.market_data.get_last_prices(instrument_id=[uid], )
        ints_info = await client.instruments.get_instrument_by(id=uid, id_type=INSTRUMENT_ID_TYPE_UID)
        lot = ints_info.instrument.lot
        min_price_increment = quotation_to_decimal(ints_info.instrument.min_price_increment)
        last_price = quotation_to_decimal(r.last_prices[0].price)
        buy_price = last_price * settings.COEFICIENT_LIMIT_ORDER // min_price_increment * min_price_increment
        amount = int(bid // buy_price)
        price = decimal_to_quotation(buy_price)
        loguru.logger.info(f"{direction} {amount} shares for {price} RUB")
        direction = OrderDirection.ORDER_DIRECTION_BUY if direction == 'buy' else OrderDirection.ORDER_DIRECTION_SELL
        await client.orders.post_order(instrument_id=uid,
                                       account_id=account_id,
                                       quantity=amount,
                                       price=price,
                                       order_type=OrderType.ORDER_TYPE_LIMIT,
                                       direction=direction)
    return buy_price, amount


async def get_orders(token, account_id) -> List[Order]:
    async with AsyncClient(token) as client:
        r = await client.orders.get_orders(account_id=account_id)
        return r.orders
