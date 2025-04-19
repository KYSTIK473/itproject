from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db import new_session, FilmOrm, UserOrm, Token
from schemas import FilmAdd, UserAdd, TokenCreate, TokenUpdate


class TaskRep:
    @classmethod
    async def add_one(cls, data: FilmAdd) -> int:
        async with new_session() as session:
            film_dict = data.model_dump()
            film = FilmOrm(**film_dict)
            session.add(film)
            await session.flush()
            await session.commit()
            return film.id
    @classmethod
    async def find_all(cls):
        async with new_session() as session:
            query = select(FilmOrm)
            result = await session.execute(query)
            film_models = result.scalars().all()
            return film_models

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
    async def find_one_or_none(cls, email: str) -> UserOrm | None:
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.email == email)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_id(cls, user_id: int) -> UserOrm | None:
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
    async def find_one_or_none(cls, token: str) -> Token | None:
        async with new_session() as session:
            query = select(Token).where(Token.token == token)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_user_id(cls, user_id: int) -> Token | None:
        """Поиск токена по ID пользователя"""
        async with new_session() as session:
            query = select(Token).where(Token.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_token(cls, token: str) -> Token | None:
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