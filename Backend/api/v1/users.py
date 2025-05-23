from app.core.config import settings
from app.repositories.tokens import TokenRep
from app.repositories.users import UserRep
from app.schemas.users import UserUpdate

from fastapi import Request, HTTPException, APIRouter

usr = APIRouter()

@usr.get("/user_data/")
async def user_data(request: Request) -> dict:
    token = request.cookies.get(settings.JWT_ACCESS_COOKIE_NAME)
    user = await TokenRep.find_by_token(token)
    user_data = await UserRep.find_by_id(user.id)
    return {
        "message": "Данные пользователя",
        "user_id": user_data.id,
        "email": user_data.email,
        "phone": user_data.phone_number,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,  # если используется JWT
    }


@usr.patch("/update_user_data/")
async def update_user_data(request: Request,
                           update_data: UserUpdate,
                           ):
    # Преобразуем Pydantic модель в dict, исключая неустановленные поля
    update_dict = update_data.dict(exclude_unset=True)
    token = request.cookies.get(settings.JWT_ACCESS_COOKIE_NAME)
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