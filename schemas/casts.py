from pydantic import BaseModel
from typing import Optional


class CastBase(BaseModel):
    movie_id: Optional[int] = None
    cast_id: Optional[int] = None
    character: Optional[str] = None
    credit_id: Optional[str] = None
    gender: Optional[int] = None
    id_person: Optional[int] = None
    name: Optional[str] = None
    order: Optional[int] = None


class CastCreate(CastBase):
    pass


class Cast(CastBase):
    class Config:
        orm_mode = True
