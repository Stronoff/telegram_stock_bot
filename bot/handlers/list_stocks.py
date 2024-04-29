from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline.stocks import stock_list_choose_acc
from bot.services.users import get_user_token
from bot.services.stock_user_info import list_accounts


router = Router(name="list_stocks")


@router.callback_query(F.data == 'list_stocks')
async def process_list_stocks(callback: CallbackQuery, session: AsyncSession):
    token: str = await get_user_token(session, callback.message.chat.id)
    acc = await list_accounts(token)
    await callback.message.edit_text(f"Choose account",
                                     reply_markup=stock_list_choose_acc(acc))
    await callback.answer()
