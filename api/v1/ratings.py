from time import time

from fastapi import HTTPException, APIRouter, Query

from app.core.config import settings
from app.repositories.films import FilmRepository
from app.repositories.ratings import ratingRep
from app.repositories.tokens import TokenRep
from app.repositories.users import UserRep
from fastapi import Request

from app.schemas.ratings import ratingBase

rtng = APIRouter()


@rtng.post("/like")
async def like_film(
        request: Request,
        rating: float = Query(..., title="Оценка", description="Оценка фильма от 1 до 10", gt=0, le=10,
                              alias="raiting"),  # валидация: 0
        # < rating <= 10
        film_id: int = Query(..., title="ID фильма", description="ID фильма в базе данных", gt=0, alias="film_id")
        # валидация: film_id
        # > 0
):
    try:
        token = request.cookies.get(settings.JWT_ACCESS_COOKIE_NAME)
        user = await TokenRep.find_by_token(token)
        gol = user.id
        gol = int(gol)
        user_data = await UserRep.find_by_id(gol)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"Войдите в аккаунт"
        )
    like_data = ratingBase()

    like_data.userid = user_data.id
    like_data.movieid = film_id
    like_data.rating = rating
    like_data.timestamp = int(time())
    like = await ratingRep.add_one(like_data)
    if like == 'new':
        film = await FilmRepository.increment_vote_count_by_id(film_id)
        if film is None:
            raise HTTPException(
                status_code=404,
                detail=f"Фильм с ID {film_id} не найден"
            )
    return {
        "message": "Like",
        "user": like,
    }


@rtng.get("/user_rating")
async def get_user_movie_rating(
        request: Request,
        film_id: int = Query(..., title="ID фильма", description="ID фильма в базе данных", gt=0, alias="film_id")
):
    try:
        token = request.cookies.get(settings.JWT_ACCESS_COOKIE_NAME)
        user = await TokenRep.find_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Требуется авторизация")

        rating = await ratingRep.get_user_rating_for_movie(
            userid=user.id,
            movieid=film_id
        )

        if not rating:
            return {"message": "Пользователь не оценивал этот фильм"}

        return {
            "rating": rating.rating,
            "rated_at": rating.timestamp
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
