from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.crew import CrewRepository
from app.schemas.crew import CrewResponse
from typing import List

router = APIRouter(prefix="/crew", tags=["Crew"])


@router.get("/", response_model=List[CrewResponse])
async def get_crew_by_movie(
        movie_id: int
):
    try:
        crew = await CrewRepository.get_by_movie_id(movie_id)
        if not crew:
            raise HTTPException(
                status_code=404,
                detail=f"No crew found for movie with id {movie_id}"
            )
        return crew
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
