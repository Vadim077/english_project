from pydantic import BaseModel, EmailStr
from typing import Optional

# Схема для создания пользователя
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    level: Optional[str] = "A1"

# Схема для логина
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Схема для возврата данных пользователя
class UserOut(BaseModel):
    id: int
    email: EmailStr
    level: str

    class Config:
        from_attributes = True

# Схема для токена доступа
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None