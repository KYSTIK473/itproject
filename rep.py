from sqlalchemy import select, update, insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from db import new_session, FilmOrm, UserOrm, Token, RaitingOrm
from schemas import FilmAdd, UserAdd, TokenCreate, TokenUpdate, RaitingBase
import time

class FilmRepository:
    @staticmethod
    async def get_first_n_films(
            n: int = 10,
            skip: int = 0
    ) -> List[FilmOrm]:
        """
        Получает первые N фильмов из БД с возможностью пропустить первые skip записей

        :param db: Асинхронная сессия БД
        :param n: Количество записей для получения
        :param skip: Количество записей для пропуска
        :return: Список фильмов
        """
        async with new_session() as session:
            result = await session.execute(
                select(FilmOrm).order_by(FilmOrm.id).offset(skip).limit(n)
            )
            return result.scalars().all()

    @staticmethod
    async def get_film_by_id(
            film_id: int
    ) -> Optional[FilmOrm]:
        """
        Получает один фильм из БД по его идентификатору

        :param film_id: Идентификатор фильма
        :return: Объект фильма или None, если не найден
        """
        async with new_session() as session:
            result = await session.execute(
                select(FilmOrm).where(FilmOrm.id == film_id)
            )
            return result.scalars().first()

    @staticmethod
    async def increment_vote_count_by_id(
            film_id: int
    ) -> Optional[FilmOrm]:
        """
        Увеличивает счетчик голосов (vote_count) на 1 для указанного фильма

        :param film_id: Идентификатор фильма
        :return: Обновленный объект фильма или None, если не найден
        """
        async with new_session() as session:
            # Получаем фильм
            result = await session.execute(
                select(FilmOrm).where(FilmOrm.id == film_id)
            )
            film = result.scalars().first()

            if film is not None:
                # Увеличиваем vote_count на 1
                film.vote_count += 1
                await session.commit()
                await session.refresh(film)

            return film

class RaitingRep:
    @staticmethod
    async def add_one(raiting_data: RaitingBase) -> RaitingOrm:
        async with new_session() as session:
            # Проверяем, есть ли уже оценка от этого пользователя для этого фильма
            try:
                existing_rating = await session.execute(
                    select(RaitingOrm)
                        .where(
                        (RaitingOrm.user_id == raiting_data.user_id) &
                        (RaitingOrm.movie_id == raiting_data.movie_id)
                    )
                )
                existing_rating = existing_rating.scalar_one()

                # Если запись существует - обновляем её
                await session.execute(
                    update(RaitingOrm)
                        .where(RaitingOrm.id == existing_rating.id)
                        .values(
                        raiting=raiting_data.raiting,
                        timestamp=raiting_data.timestamp
                    )
                )
                await session.commit()
                await session.refresh(existing_rating)
                return existing_rating

            except NoResultFound:
                # Если записи нет - создаём новую
                stmt = (
                    insert(RaitingOrm)
                        .values(**raiting_data.model_dump())
                        .returning(RaitingOrm)
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.scalar_one()

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


class TokenRep:
    @classmethod
    async def add_one(cls, token_data: TokenCreate) -> int:
        async with new_session() as session:
            token_dict = token_data.model_dump()
            token = Token(**token_dict)
            session.add(token)
            await session.flush()
            await session.commit()
            return token


    @classmethod
    async def find_one_or_none(cls, token: str) -> Token:
        async with new_session() as session:
            query = select(Token).where(Token.token == token)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_user_id(cls, user_id: int) -> Token:
        """Поиск токена по ID пользователя"""
        async with new_session() as session:
            query = select(Token).where(Token.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_token(cls, token: str) -> Token:
        """Поиск токена по ID пользователя"""
        async with new_session() as session:
            query = select(Token).where(Token.token == token)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def update_token(cls, user_id: int, token_data: TokenUpdate) -> Token:
        """Обновление токена для пользователя"""
        async with new_session() as session:
            # Сначала проверяем существование токена
            existing_token = await cls.find_by_user_id(user_id)
            if not existing_token:
                raise ValueError("Token not found for this user")
            stmt = (update(Token)
                .where(Token.user_id == user_id)
                .values(**token_data.model_dump())
                .returning(Token)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.scalars().one()

    @classmethod
    async def upsert_token(cls, user_id: int, token: str) -> Token:
        """Обновление существующего токена или создание нового"""
        token_data = TokenCreate(user_id=user_id, token=token)
        async with new_session() as session:
            existing_token = await cls.find_by_user_id(user_id)
            if existing_token:
                # Если токен существует - обновляем
                return await cls.update_token(user_id, token_data)
            else:
                # Если токена нет - создаем новый
                return await cls.add_one(token_data)