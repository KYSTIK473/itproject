from datetime import datetime
import time
from typing import List, Optional
from fastapi import Query, HTTPException, APIRouter

from app.ML.get_n_predictions import get_n_predictions
from app.db.models import FilmOrm
from app.repositories.films import FilmRepository
from app.schemas.films import FilmBase
from app.core.config import settings
import aiohttp

flm = APIRouter()
APIKEY = settings.POSTER_API_KEY
@flm.get("/films", response_model=List[FilmBase])
async def get_films(
        limit: int = Query(10, description="Количество записей", gt=0, le=100),
        skip: int = Query(0, description="Пропустить первые N записей", ge=0),
        query: Optional[str] = Query(None, description="Поисковый запрос по названию фильма")
):
    """
    Получить первые N фильмов с возможностью пагинации и поиска.

    - **limit**: Количество возвращаемых записей (по умолчанию 10, максимум 100)
    - **skip**: Количество пропускаемых записей (для пагинации)
    - **query**: Строка для поиска по названию фильма (опционально)
    """
    films = await FilmRepository.get_first_n_films(n=limit, skip=skip, search_query=query)
    return films


@flm.get("/get_poster_link")
async def poster_link(film_id: int):
    film = await FilmRepository.get_film_by_id(film_id)
    imdb_id = film.imdb_id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.omdbapi.com/?i={imdb_id}&apikey={APIKEY}") as response:
            data_link = await response.json()

    return {
        "poster_link": data_link["Poster"]
    }


@flm.get("/get_film_by_id", response_model=FilmBase)
async def get_film_by_id(
        film_id: int) -> Optional[FilmOrm]:
    """
    Получить фильм по его ID

    Args:
        film_id (int): ID фильма

    Returns:
        FilmOrm: Объект фильма

    Raises:
        HTTPException: 404 если фильм не найден
    """
    film = await FilmRepository.get_film_by_id(film_id)

    if film is None:
        raise HTTPException(
            status_code=404,
            detail=f"Фильм с ID {film_id} не найден"
        )
    return film


@flm.get("/get_similarity")
async def get_similarity(
        film_id: int
):
    list_predictions = get_n_predictions(film_id, 5)
    list_response = []
    for i in list_predictions:
        film = await FilmRepository.get_film_by_id(i)
        try:
            times = int(film.release_date)
            release_date = datetime.fromtimestamp(times).strftime("%Y-%m-%d")
            film.release_date = release_date
        except Exception:
            film.release_date = '-'
            print('oops')

        list_response.append(film)
    return list_response