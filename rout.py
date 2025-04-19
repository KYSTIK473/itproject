from typing import Annotated

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette.responses import JSONResponse

from rep import TaskRep, UserRep, TokenRep
from schemas import FilmAdd, UserAdd, UserLogin, TokenCreate
from password import get_password_hash, verify_password

from authx import AuthX, AuthXConfig

goida = APIRouter()

@goida.post("/film")
async def add_film(film: Annotated[FilmAdd, Depends()]):
    film_id = await TaskRep.add_one(film)
    return {"ok": True, "tsk_id": film_id}


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
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    token_get = await TokenRep.upsert_token(user.id, token)
    return {
        "message": "Вы успешно авторизованы!",
        "user_id": user.id,
        "access_token": token_get.token,  # если используется JWT
    }

@goida.post("/user_data/")
async def user_data(request: Request) -> dict:
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    user = await TokenRep.find_by_token(token)
    #print(user)
    #print(user.user_id)
    #print(user.id)
    gol = user.id
    #print(gol)
    gol = int(gol)
    user_data = await UserRep.find_by_id(gol)
    #print(user_data)
    return {
        "message": "Данные пользователя",
        "user_id": user_data.id,
        "email": user_data.email,  # если используется JWT
    }

@goida.post("/user_update_data/")
async def user_update_data(request: Request) -> dict:
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    user = await TokenRep.find_by_token(token)
    gol = user.id
    gol = int(gol)
    user_data = await UserRep.find_by_id(gol)
    return {
        "message": "Данные пользователя",
        "user_id": user_data.id,
        "email": user_data.email,  # если используется JWT
    }

@goida.get("/film")
async def get_films():
    film_data = await TaskRep.find_all()
    return {"data": film_data}

@goida.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return JSONResponse({'sucsess': True})

