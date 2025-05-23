from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import CrewOrm
from app.db.setup import new_session
from app.schemas.crew import CrewResponse
from typing import List


class CrewRepository:
    @staticmethod
    async def get_by_movie_id(movie_id: int) -> List[CrewOrm]:
        async with new_session() as session:
            stmt = select(CrewOrm).where(CrewOrm.movie_id == movie_id).limit(5)
            result = await session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    async def get_by_movie_id_as_dict(movie_id: int) -> List[dict]:
        async with new_session() as session:
            crews = await CrewRepository.get_by_movie_id(movie_id)
            return [CrewResponse.model_validate(crew).model_dump() for crew in crews]
