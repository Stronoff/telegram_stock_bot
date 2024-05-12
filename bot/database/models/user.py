# ruff: noqa: TCH001, TCH003, A003, F821
from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base, created_at, int_pk


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None]
    language_code: Mapped[str | None]
    created_at: Mapped[created_at]
    tinkoff_token: Mapped[str | None]
    account_id: Mapped[int | None]
    is_admin: Mapped[bool] = mapped_column(default=False)
