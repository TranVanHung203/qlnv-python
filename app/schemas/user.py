from pydantic import EmailStr, Field, constr
from typing import Optional, List, Literal
from datetime import datetime
from .auth import CamelModel


class CreateUserDto(CamelModel):
    username: constr(min_length=1, max_length=50)
    email: EmailStr
    password: constr(min_length=6)
    full_name: Optional[constr(min_length=1, max_length=100)] = None
    role: Optional[Literal['Admin', 'Assistant']] = None


class UpdateUserDto(CamelModel):
    # id is provided in the path; request body only contains updatable fields
    full_name: Optional[constr(min_length=1, max_length=100)] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal['Admin', 'Assistant']] = None


class UserDto(CamelModel):
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str


class PagedResult(CamelModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    items: List[UserDto]
