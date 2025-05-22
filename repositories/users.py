from typing import Optional, List

from sqlalchemy import select

from app.db.models import FilmOrm, UserOrm
from app.db.setup import new_session
from app.schemas.users import UserAdd


class UserRep:
    @classmethod
    async def add_one(cls, data: UserAdd) -> int:
        async with new_session() as session:
            film_dict = data.model_dump()
            film = UserOrm(**film_dict)
            session.add(film)
            await session.flush()
            await session.commit()
            return film.id

    @classmethod
    async def find_all(cls):
        async with new_session() as session:
            query = select(UserOrm)
            result = await session.execute(query)
            film_models = result.scalars().all()
            return film_models

    @classmethod
    async def find_one_or_none(cls, email: str) -> UserOrm:
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.email == email)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_id(cls, user_id: int) -> UserOrm:
        async with new_session() as session:
            # Явно преобразуем user_id в int на случай, если пришло что-то другое
            user_id = int(user_id)

            # Альтернативный вариант 1: используем session.get()
            user = await session.get(UserOrm, user_id)
            return user

            # Или альтернативный вариант 2: используем правильный select
            # query = select(UserOrm).where(UserOrm.id == user_id)
            # result = await session.execute(query)
            # return result.scalars().first()

    @classmethod
    async def update_user(cls, user_id: int, update_data: dict) -> UserOrm:
        async with new_session() as session:
            # Получаем пользователя
            user = await session.get(UserOrm, user_id)
            if not user:
                return None

            # Обновляем только переданные поля
            for key, value in update_data.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)

            await session.commit()
            await session.refresh(user)
            return user