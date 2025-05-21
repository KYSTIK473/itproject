from typing import Optional
from datetime import date
from pydantic import BaseModel
from typing import Optional, List, Dict

class FilmBase(BaseModel):
    budget: Optional[float] = None
    movie_id: Optional[int] = None
    imdb_id: Optional[str] = None
    original_language: Optional[str] = None
    overview: Optional[str] = None
    popularity: Optional[float] = None
    release_date: Optional[date] = None
    revenue: Optional[float] = None
    runtime: Optional[int] = None
    status: Optional[str] = None
    tagline: Optional[str] = None
    title: str
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    genres: Optional[List[str]] = None
    spoken_languages: Optional[List[str]] = None
    production_companies: Optional[List[str]] = None
    adult: Optional[bool] = None


class FilmAdd(FilmBase):
    pass


class FilmUpdate(BaseModel):
    budget: Optional[float] = None
    overview: Optional[str] = None
    popularity: Optional[float] = None
    # ... другие поля, которые можно обновлять


class Film(FilmBase):
    id: int

    class Config:
        from_attributes = True

class UserAdd(BaseModel):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    email: str
    password: str
    #avatar_url


class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str

class TokenCreate(BaseModel):
    token: str
    user_id: int

class Token(TokenCreate):
    id: int

class TokenUpdate(BaseModel):
    token: str


class RaitingBase(BaseModel):
    user_id: Optional[int] = None
    movie_id: Optional[int] = None
    raiting: Optional[float] = None
    timestamp: Optional[float] = None


class Raiting(RaitingBase):
    id: int