from datetime import date

from pydantic import BaseModel
from typing import Optional, List


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




class Film(FilmBase):
    id: int
    avg_rating: Optional[float] = None

    class Config:
        orm_mode = True