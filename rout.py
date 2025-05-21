from time import time
from typing import Annotated, Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter, Response, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from starlette.responses import JSONResponse

from db import FilmOrm
from rep import FilmRepository, UserRep, TokenRep, RaitingRep
from schemas import FilmAdd, UserAdd, UserLogin, TokenCreate, UserUpdate, FilmBase, RaitingBase
from password import get_password_hash, verify_password
from typing import List
from authx import AuthX, AuthXConfig

goida = APIRouter()


@goida.get("/films", response_model=List[FilmBase])
async def get_films(
        limit: int = Query(10, description="Количество записей", gt=0, le=100),
        skip: int = Query(0, description="Пропустить первые N записей", ge=0),
):
    """
    Получить первые N фильмов с возможностью пагинации

    - **limit**: Количество возвращаемых записей (по умолчанию 10, максимум 100)
    - **skip**: Количество пропускаемых записей (для пагинации)
    """
    films = await FilmRepository.get_first_n_films(n=limit, skip=skip)
    """for i in films:
        i.genres = ''.join(i.genres).strip('{').strip('}').split(',')"""
    return films


@goida.get("/get_film_by_id", response_model=FilmBase)
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

@goida.post("/like")
async def like_film(raiting: float, film_id: int, request: Request):
    try:
        token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
        user = await TokenRep.find_by_token(token)
        gol = user.id
        gol = int(gol)
        user_data = await UserRep.find_by_id(gol)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"Войдите в аккаунт"
        )
    film = await FilmRepository.increment_vote_count_by_id(film_id)
    if film is None:
        raise HTTPException(
            status_code=404,
            detail=f"Фильм с ID {film_id} не найден"
        )
    like_data = RaitingBase()

    like_data.user_id = user_data.id
    like_data.movie_id = film_id
    like_data.raiting = raiting
    like_data.timestamp = int(time())
    like = await RaitingRep.add_one(like_data)
    return {
        "message": "Like",
        "user": like,
    }

@goida.post("/register/")
async def register_user(user_data: UserAdd) -> dict:
    user = await UserRep.find_one_or_none(email=user_data.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail='Пользователь уже существует'
        )
    user_dict = user_data
    user_dict.password = get_password_hash(user_data.password)
    user_id = await UserRep.add_one(user_dict)
    return {'message': 'Вы успешно зарегистрированы!', "id": user_id}

config = AuthXConfig()
#.env
config.JWT_SECRET_KEY = 'secret' # .env
config.JWT_ACCESS_COOKIE_NAME = 'my_acsess_token'
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)


@goida.post("/login/")
async def login_user(login_data: UserLogin, response: Response) -> dict:
    # Ищем пользователя по email
    user = await UserRep.find_one_or_none(email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль"
        )

    # Проверяем пароль
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль"
        )

    #token = security.create_access_token(uid=user.id)
    print(user.id)
    token = security.create_access_token(uid=str(user.id))
    response.set_cookie(
        key=f"{config.JWT_ACCESS_COOKIE_NAME}",
        value=f"{token}",  # Для HTTP
        httponly=True,
        secure=False,  # False для localhost, True для production с HTTPS
        samesite="lax",  # или "none" если нужен кросс-сайтовый доступ
        max_age=3600,  # Время жизни куки в секундах
        path="/",
    )
    token_get = await TokenRep.upsert_token(user.id, token)
    return {
        "message": "Вы успешно авторизованы!",
        "user_id": user.id,
        "access_token": token_get.token,  # если используется JWT
    }


@goida.post("/logout/")
async def logout_user(response: Response) -> dict:
    # Удаляем куки с токеном
    response.delete_cookie(
        key=f"{config.JWT_ACCESS_COOKIE_NAME}",
        path="/",
    )

    # Если нужно также удалить токен из базы данных
    # (раскомментируйте если используете это)
    # user_id = ... # Получить ID пользователя из текущего запроса
    # await TokenRep.delete_token(user_id)

    return {
        "message": "Вы успешно вышли из системы",
        "success": True
    }


@goida.get("/check_auth")
async def check_auth(request: Request):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        return {"is_authenticated": False}

    user = await TokenRep.find_by_token(token)
    if not user:
        return {"is_authenticated": False}

    #user_data = await UserRep.find_by_id(user.user_id)
    return {
        "is_authenticated": True
    }


@goida.get("/user_data/")
async def user_data(request: Request) -> dict:
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    user = await TokenRep.find_by_token(token)
    gol = user.id
    gol = int(gol)
    user_data = await UserRep.find_by_id(gol)
    return {
        "message": "Данные пользователя",
        "user_id": user_data.id,
        "email": user_data.email,
        "phone": user_data.phone_number,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name, # если используется JWT
    }


@goida.patch("/update_user_data/")
async def update_user_data(request: Request,
        update_data: UserUpdate,
):
    # Преобразуем Pydantic модель в dict, исключая неустановленные поля
    update_dict = update_data.dict(exclude_unset=True)
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        return {"is_authenticated": False}

    user = await TokenRep.find_by_token(token)
    if not user:
        return {"is_authenticated": False}
    user_id = user.user_id
    updated_user = await UserRep.update_user(user_id, update_dict)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user



@goida.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return JSONResponse({'sucsess': True})

