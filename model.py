from pydantic import BaseModel
from typing import Optional


class FilmBase(BaseModel):
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    director: Optional[str] = None


class FilmCreate(FilmBase):
    pass


class Film(FilmBase):
    id: int
    avg_rating: Optional[float] = None

    class Config:
        orm_mode = True


class RatingBase(BaseModel):
    film_id: int
    rating: float


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None