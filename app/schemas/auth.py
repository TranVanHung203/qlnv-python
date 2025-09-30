from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Callable


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + ''.join(p.title() for p in parts[1:])


class CamelModel(BaseModel):
    class Config:
        alias_generator: Callable[[str], str] = to_camel
        # Pydantic v2 config keys
        validate_by_name = True
        from_attributes = True


class LoginDto(CamelModel):
    username: str
    password: str


class AuthResponseDto(CamelModel):
    token: str
    refresh_token: str
    expiration: datetime


class RefreshTokenRequestDto(CamelModel):
    refresh_token: str


class ForgotPasswordDto(CamelModel):
    email: EmailStr


class ResetPasswordDto(CamelModel):
    email: EmailStr
    token: str
    new_password: str = Field(min_length=6)
