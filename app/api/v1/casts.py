from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.repositories.casts import CastRepository
from app.schemas.casts import CastBase

router = APIRouter()


@router.get("/cast")
async def get_cast_by_movie(
        movie_id: int
):
    try:
        crew = await CastRepository.get_by_movie_id(movie_id)
        if not crew:
            raise HTTPException(
                status_code=404,
                detail=f"No crew found for movie with id {movie_id}"
            )
        return crew
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
