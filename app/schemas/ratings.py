from pydantic import BaseModel
from typing import Optional


class ratingBase(BaseModel):
    userid: Optional[int] = None
    movieid: Optional[int] = None
    rating: Optional[float] = None
    timestamp: Optional[float] = None


class rating(ratingBase):
    id: int