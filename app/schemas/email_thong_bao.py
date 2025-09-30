from pydantic import Field, EmailStr
from typing import Optional, List
from .auth import CamelModel


class CreateEmailThongBaoDto(CamelModel):
    email: EmailStr
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)


class UpdateEmailThongBaoDto(CamelModel):
    id: int
    email: EmailStr
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)


class EmailThongBaoDto(CamelModel):
    id: int
    email: EmailStr
    name: Optional[str] = None


class PagedEmailThongBaoResult(CamelModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    items: List[EmailThongBaoDto]
