from typing import List, Dict

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


def stock_list_choose_acc(accounts: List[Dict]) -> InlineKeyboardMarkup:
    """Use in start process."""
    buttons = [
        [InlineKeyboardButton(text=_(f"{a['name']}"), callback_data=f"set-account-id_{a['id']}") for a in accounts],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    keyboard.adjust(1, 1, 2)

    return keyboard.as_markup()
