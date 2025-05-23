from fastapi import HTTPException, Response, Request, APIRouter

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, security
from app.repositories.tokens import TokenRep
from app.repositories.users import UserRep
from app.schemas.users import UserAdd, UserLogin

auth = APIRouter()

@auth.post("/register/")
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

@auth.post("/login/")
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

    # token = security.create_access_token(uid=user.id)
    #print(user.id)
    token = security.create_access_token(uid=str(user.id))
    response.set_cookie(
        key=f"{settings.JWT_ACCESS_COOKIE_NAME}",
        value=f"{token}",  # Для HTTP
        httponly=True,
        secure=False,  # False для localhost, True для production с HTTPS
        samesite="lax",  # или "none" если нужен кросс-сайтовый доступ
        max_age=3600,  # Время жизни куки в секундах
        path="/",
    )
    token_get = await TokenRep.upsert_token(user.id, token)
    print(token_get.token)
    return {
        "message": "Вы успешно авторизованы!",
        "user_id": user.id,
        "access_token": token_get.token,  # если используется JWT
    }


@auth.post("/logout/")
async def logout_user(response: Response) -> dict:
    # Удаляем куки с токеном
    response.delete_cookie(
        key=f"{settings.JWT_ACCESS_COOKIE_NAME}",
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


@auth.get("/check_auth")
async def check_auth(request: Request):
    token = request.cookies.get(settings.JWT_ACCESS_COOKIE_NAME)
    if not token:
        return {"is_authenticated": False}

    user = await TokenRep.find_by_token(token)
    if not user:
        return {"is_authenticated": False}

    # user_data = await UserRep.find_by_id(user.user_id)
    return {
        "is_authenticated": True
    }