from pydantic import BaseModel
from typing import Optional

class UserAdd(BaseModel):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    email: str
    password: str
    #avatar_url


class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str