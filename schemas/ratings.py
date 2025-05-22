from pydantic import BaseModel
from typing import Optional


class ratingBase(BaseModel):
    user_id: Optional[int] = None
    movie_id: Optional[int] = None
    rating: Optional[float] = None
    timestamp: Optional[float] = None


class rating(ratingBase):
    id: int