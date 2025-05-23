from pydantic import BaseModel
from typing import Optional


class TokenCreate(BaseModel):
    token: str
    user_id: int


class Token(TokenCreate):
    id: int


class TokenUpdate(BaseModel):
    token: str
