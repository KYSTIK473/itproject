from pydantic import BaseModel
from typing import Optional


class CrewBase(BaseModel):
    movie_id: int
    credit_id: str
    department: Optional[str] = None
    gender: Optional[int] = None
    person_id: Optional[int] = None
    job: Optional[str] = None
    name: str

    class Config:
        from_attributes = True


class CrewResponse(CrewBase):
    id: int
