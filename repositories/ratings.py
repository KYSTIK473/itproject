from typing import Optional

from sqlalchemy import insert, update, select
from sqlalchemy.exc import NoResultFound

from app.db.models import ratingOrm
from app.db.setup import new_session
from app.schemas.ratings import ratingBase


class ratingRep:
    @staticmethod
    async def add_one(rating_data: ratingBase) -> ratingOrm:
        async with new_session() as session:
            # Проверяем, есть ли уже оценка от этого пользователя для этого фильма
            try:
                existing_rating = await session.execute(
                    select(ratingOrm)
                        .where(
                        (ratingOrm.userid == rating_data.userid) &
                        (ratingOrm.movieid == rating_data.movieid)
                    )
                )
                existing_rating = existing_rating.scalar_one()

                # Если запись существует - обновляем её
                await session.execute(
                    update(ratingOrm)
                        .where(ratingOrm.id == existing_rating.id)
                        .values(
                        rating=rating_data.rating,
                        timestamp=rating_data.timestamp
                    )
                )
                await session.commit()
                await session.refresh(existing_rating)
                return 'upload'

            except NoResultFound:
                # Если записи нет - создаём новую
                stmt = (
                    insert(ratingOrm)
                        .values(**rating_data.model_dump())
                       .returning(ratingOrm)
                )
                result = await session.execute(stmt)
                await session.commit()
                return 'new'


    @staticmethod
    async def get_user_rating_for_movie(
            userid: int,
            movieid: int
    ) -> Optional[ratingOrm]:
        """
        Получить оценку пользователя для конкретного фильма

        Args:
            session: AsyncSession - асинхронная сессия SQLAlchemy
            userid: int - ID пользователя
            movieid: int - ID фильма

        Returns:
            Optional[ratingOrm] - объект оценки или None если оценка не найдена
        """
        async with new_session() as session:
            stmt = select(ratingOrm).where(
                (ratingOrm.userid == userid) &
                (ratingOrm.movieid == movieid)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
