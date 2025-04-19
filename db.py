from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column
from sqlalchemy import text



eng = create_async_engine(
    "sqlite+aiosqlite:///films.db"
)

new_session = async_sessionmaker(eng, expire_on_commit=False)

class Model(DeclarativeBase):
    pass

class FilmOrm(Model):
    __tablename__ = 'films'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[Optional[str]]
    year: Mapped[Optional[int]]
    director: Mapped[Optional[str]]
    average_rating: Mapped[Optional[float]]

class UserOrm(Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    #tokens = relationship("Token", back_populates='users')

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class Token(Model):
    __tablename__ = 'tokens'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = Mapped[str]
    token: Mapped[str]
    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

async def create_tables():
    async with eng.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
    async with eng.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
