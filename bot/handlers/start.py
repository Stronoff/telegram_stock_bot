from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline.menu import main_keyboard
from bot.keyboards.inline.stocks import stock_list_choose_acc
from bot.services.stock_user_info import list_accounts
from bot.services.users import update_user_token, update_user_account_id

router = Router(name="start")


class UserInfo(StatesGroup):
    token = State()
    accounts = State()


@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    """Welcome message."""
    await message.answer(_("Для начала необходим привязать аккаунт Тинькофф.\nВведите TOKEN"),
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserInfo.token)


@router.message(F.text, UserInfo.token)
async def save_token(message: types.Message, session: AsyncSession, state: FSMContext) -> None:
    await state.update_data(token=message.text)
    await update_user_token(session, message.from_user.id, message.text)
    a = await list_accounts(message.text)
    await message.answer(f"Your token has been saved! You can change token by using command /start again")
    await message.answer("Выберете аккаунт для торговли/мониторинга", reply_markup=stock_list_choose_acc(a))
    await state.clear()


@router.callback_query(F.data.startswith('set-account-id'))
async def process_select_account(callback: CallbackQuery, session: AsyncSession) -> None:
    account_id = callback.data.split('_')[1]
    account_name = filter(lambda x: x[0].callback_data == F.data, callback.message.reply_markup.inline_keyboard)
    await update_user_account_id(session, callback.message.chat.id, account_id)
    await callback.message.edit_text(
        f"Selected account_id: {account_id}\nName: {list(account_name)[0][0].text}",
        reply_markup=main_keyboard())
    await callback.answer()
