from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column
from sqlalchemy import Float, Integer, String, Boolean, Text, ARRAY, Column, Date
from sqlalchemy.ext.asyncio import AsyncAttrs


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
    release_date: Mapped[Optional[str]] = mapped_column(Date)  # Или Date если нужно
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


class ratingOrm(Model):
    __tablename__ = "rating"
    # Автоинкрементный ID как первый столбец
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userid: Mapped[Optional[int]] = mapped_column(Integer)
    movieid: Mapped[Optional[int]] = mapped_column(Integer)
    rating: Mapped[Optional[float]] = Column(Float)
    timestamp: Mapped[Optional[int]] = Column(Integer)


class UserOrm(Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(512))
    password: Mapped[str] = mapped_column(String(512))
    # tokens = relationship("Token", back_populates='users')

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class LikeUser(UserOrm):
    likes: Mapped[Optional[str]] = Column(ARRAY(Integer))


class TokenORM(Model):
    __tablename__ = 'tokens'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    token: Mapped[str] = mapped_column(String(512))
    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class CrewOrm(Model):
    __tablename__ = "crew"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(Integer, nullable=True)
    credit_id: Mapped[str] = mapped_column(String(100), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    gender: Mapped[int] = mapped_column(Integer, nullable=True)
    person_id: Mapped[int] = mapped_column(Integer, nullable=True)
    job: Mapped[str] = mapped_column(String(200), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=True)


class CastOrm(Model):
    __tablename__ = "cast"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, nullable=True)
    cast_id = Column(Integer, nullable=True)
    character = Column(String, nullable=True)
    credit_id = Column(String, nullable=True)
    gender = Column(Integer, nullable=True)
    id_person = Column(Integer, nullable=True)
    name = Column(String, nullable=True)
    order = Column(Integer, nullable=True)
