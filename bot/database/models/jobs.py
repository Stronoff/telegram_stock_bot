# ruff: noqa: TCH001, TCH003, A003, F821
from __future__ import annotations

from sqlalchemy.orm import Mapped

from bot.database.models.base import Base, int_pk


class JobModel(Base):
    __tablename__ = "jobs"

    id: Mapped[int_pk]
    job_id: Mapped[str]
    job_name: Mapped[str]
