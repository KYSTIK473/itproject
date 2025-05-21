import json
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column
from sqlalchemy import JSON, Float, Integer, String, Boolean, Date, event, Text, ARRAY, Column
from sqlalchemy.ext.asyncio import AsyncAttrs


# Изменение строки подключения для PostgreSQL
eng = create_async_engine(
    "postgresql+asyncpg://user:123@localhost:5432/films"
    # Замените username, password и dbname на ваши реальные данные
)

new_session = async_sessionmaker(eng, expire_on_commit=False)

class Model(DeclarativeBase):
    pass


class Base(AsyncAttrs, DeclarativeBase):
    pass


class FilmOrm(Model):
    __tablename__ = "films_all"

    # Автоинкрементный ID как первый столбец
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Остальные поля с правильными типами
    budget: Mapped[Optional[float]] = mapped_column(Float)
    movie_id: Mapped[Optional[int]] = mapped_column(Integer)
    imdb_id: Mapped[Optional[str]] = mapped_column(String(20))
    original_language: Mapped[Optional[str]] = mapped_column(String(10))
    overview: Mapped[Optional[str]] = mapped_column(Text)
    popularity: Mapped[Optional[float]] = mapped_column(Float)
    release_date: Mapped[Optional[str]] = mapped_column(String)  # Или Date если нужно
    revenue: Mapped[Optional[float]] = mapped_column(Float)
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String(150))
    tagline: Mapped[Optional[str]] = mapped_column(String(500))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    vote_average: Mapped[Optional[float]] = mapped_column(Float)
    vote_count: Mapped[Optional[int]] = mapped_column(Integer)
    adult: Mapped[Optional[bool]] = mapped_column(Boolean)

    # JSON-поля
    genres: Mapped[Optional[str]] = Column(ARRAY(String(500)))
    spoken_languages: Mapped[Optional[str]] = Column(ARRAY(String(500)))
    production_companies: Mapped[Optional[str]] = Column(ARRAY(String(500)))

class RaitingOrm(Model):
    __tablename__ = "raitingsss"

    # Автоинкрементный ID как первый столбец
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    movie_id: Mapped[Optional[int]] = mapped_column(Integer)
    raiting: Mapped[Optional[float]] = Column(Float)
    timestamp: Mapped[Optional[int]] = Column(Integer)

class UserOrm(Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(512))
    password: Mapped[str] = mapped_column(String(512))
    #tokens = relationship("Token", back_populates='users')

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class LikeUser(UserOrm):
    likes: Mapped[Optional[str]] = Column(ARRAY(Integer))

class Token(Model):
    __tablename__ = 'tokens'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    token: Mapped[str] = mapped_column(String(512))
    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

async def create_tables():
    async with eng.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
    async with eng.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)