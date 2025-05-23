from passlib.context import CryptContext
from authx import AuthX, AuthXConfig
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

authx_config = AuthXConfig()
authx_config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
authx_config.JWT_ACCESS_COOKIE_NAME = settings.JWT_ACCESS_COOKIE_NAME
authx_config.JWT_TOKEN_LOCATION = ["cookies"] # Из вашего rout.py

security = AuthX(config=authx_config)