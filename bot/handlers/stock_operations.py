from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.users import get_tinkoff_id
from bot.services.stock_orders import post_order, get_orders

router = Router(name="stock_operations")


@router.callback_query(F.data.startswith('stock_operation__'))
async def buy_sell_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    _, command, amount, uid = callback.data.split('__')
    user_id = callback.from_user.id
    token, account_id = await get_tinkoff_id(session, user_id)
    amount = 10000 if amount == 'X' else int(amount)
    if command in ['buy', 'sell']:
        p, a = await post_order(token, account_id, uid, amount, command)
        await callback.answer(f"Successfully {command} {a} shares for {p}")
    else:
        await callback.message.answer(f"Invalid command got in callback: {callback.data}")


@router.callback_query(F.data.startswith('get_orders'))
async def get_orders_handler(session: AsyncSession, callback: CallbackQuery):
    user_id = callback.from_user.id
    token, account_id = await get_tinkoff_id(session, user_id)
    orders = await get_orders(token, account_id)
    orders_str = '\n'.join(orders)
    msg_text = f"Orders received: {orders_str}"

    await callback.bot.send_message(user_id, msg_text)


@router.message(F.text.startswith("/get_orders"))
async def get_orders_handler(session: AsyncSession, message: types.Message = None):
    user_id = message.from_user.id
    token, account_id = await get_tinkoff_id(session, user_id)
    orders = await get_orders(token, account_id)
    orders_str = '\n'.join(orders)
    msg_text = f"Orders received: {orders_str}"

    await message.answer(msg_text)
