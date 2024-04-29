from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_keyboard() -> InlineKeyboardMarkup:
    """Use in main menu."""
    buttons = [
        [InlineKeyboardButton(text=_("Текущий портфель"), callback_data="list_stocks")],
        [InlineKeyboardButton(text=_("Активные заявки"), callback_data="list_orders")],
        [InlineKeyboardButton(text=_("Статистика по пульсу по тикеру"), callback_data="pulse_stats")],
        [InlineKeyboardButton(text=_("Подписаться на новости по тикеру"), callback_data="news_subscribe")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    keyboard.adjust(1, 1, 2)

    return keyboard.as_markup()
