from typing import Optional

from pydantic import BaseModel


class FilmAdd(BaseModel):
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    director: Optional[str] = None
    average_rating: Optional[float] = None

class Film(FilmAdd):
    id: int


class UserAdd(BaseModel):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    email: str
    password: str

class User(UserAdd):
    id: int

class UserLogin(BaseModel):
    email: str
    password: str

class TokenCreate(BaseModel):
    user_id: int
    token: str

class TokenUpdate(BaseModel):
    token: str | None = None