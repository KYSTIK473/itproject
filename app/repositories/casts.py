from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CastOrm
from app.db.setup import new_session
from app.repositories.crew import CrewRepository
from app.schemas.casts import CastBase
from app.schemas.crew import CrewResponse


class CastRepository:
    @staticmethod
    async def get_by_movie_id(movie_id: int) -> List[CastOrm]:
        async with new_session() as session:
            stmt = select(CastOrm).where(CastOrm.movie_id == movie_id).limit(5)
            result = await session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    async def get_by_movie_id_as_dict(movie_id: int) -> List[dict]:
        async with new_session() as session:
            crews = await CrewRepository.get_by_movie_id(movie_id)
            return [CrewResponse.model_validate(crew).model_dump() for crew in crews]