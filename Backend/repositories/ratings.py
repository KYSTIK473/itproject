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
                        (ratingOrm.user_id == rating_data.user_id) &
                        (ratingOrm.movie_id == rating_data.movie_id)
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
