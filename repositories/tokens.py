from sqlalchemy import select, update
from sqlalchemy.future import select as select_future

from app.db.models import TokenORM
from app.db.setup import new_session
from app.schemas.token import TokenCreate, Token, TokenUpdate


class TokenRep:
    @classmethod
    async def add_one(cls, token_data: TokenCreate) -> int:
        async with new_session() as session:
            token_dict = token_data.model_dump()
            token = TokenORM(**token_dict)
            session.add(token)
            await session.flush()
            await session.commit()
            return token.id  # Return the ID instead of the object

    @classmethod
    async def find_one_or_none(cls, token: str) -> TokenORM:
        async with new_session() as session:
            query = select(TokenORM).where(TokenORM.token == token)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_user_id(cls, user_id: int) -> TokenORM:
        """Поиск токена по ID пользователя"""
        async with new_session() as session:
            query = select(TokenORM).where(TokenORM.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_token(cls, token: str) -> TokenORM:
        """Поиск токена по самому токену"""
        async with new_session() as session:
            query = select(TokenORM).where(TokenORM.token == token)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def update_token(cls, user_id: int, token_data: TokenUpdate) -> TokenORM:
        """Обновление токена для пользователя"""
        async with new_session() as session:
            stmt = (update(TokenORM)
                .where(TokenORM.user_id == user_id)
                .values(**token_data.model_dump())
                .returning(TokenORM))
            result = await session.execute(stmt)
            await session.commit()
            return result.scalars().one()

    @classmethod
    async def upsert_token(cls, user_id: int, token: str) -> TokenORM:
        """Обновление существующего токена или создание нового"""
        token_data = TokenUpdate(token=token)  # Note: Changed to TokenUpdate
        async with new_session() as session:
            existing_token = await cls.find_by_user_id(user_id)
            if existing_token:
                return await cls.update_token(user_id, token_data)
            else:
                new_token = TokenCreate(user_id=user_id, token=token)
                return await cls.add_one(new_token)