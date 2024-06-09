from typing import List, Dict

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tinkoff.invest import InstrumentShort


def stock_list_choose_acc(accounts: List[Dict]) -> InlineKeyboardMarkup:
    """Use in start process."""
    buttons = [
        [InlineKeyboardButton(text=_(f"{a['name']}"), callback_data=f"set-account-id_{a['id']}") for a in accounts],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    keyboard.adjust(1, 1, 2)

    return keyboard.as_markup()


def buy_sell_kb(instruments_list: List[InstrumentShort], delta: List[float]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=f"{instrument.name}: {'⬆️' if delta>0 else '⬇️'} {delta}%",
                                 url=f"https://www.tinkoff.ru/invest/stocks/{instrument.ticker}/"),
            InlineKeyboardButton(text=f"Buy {instrument.ticker}", callback_data=f"stock_operation__buy__X__{instrument.uid}"),
            InlineKeyboardButton(text=f"Sell {instrument.ticker}", callback_data=f"stock_operation__sell__X__{instrument.uid}")
        ]
        for delta, instrument in zip(delta, instruments_list)]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1, 2, repeat=True)

    return keyboard.as_markup()
