from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession
from bot.services.users import get_user_token
from bot.database.models import UserModel

router = Router(name="info")


@router.message(Command(commands=["get_token"]))
async def info_handler(message: types.Message, session: AsyncSession) -> None:
    """Information about bot."""
    token = await get_user_token(session, message.from_user.id)
    await message.answer(f"Your token is {token}")
