from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import JobModel


async def add_job(session: AsyncSession, user_id: int, job_id: int, job_name: str) -> None:
    new_job = JobModel(id=user_id, job_id=job_id, job_name=job_name)
    session.add(new_job)
    await session.commit()


async def remove_job(session: AsyncSession, user_id: int, job_name: str) -> None:


    delete_stmt = delete(JobModel).where(JobModel.id == user_id).where(JobModel.job_name == job_name)

    await session.execute(delete_stmt)
    await session.commit()
    return