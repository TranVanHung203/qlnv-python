from pydantic import Field, EmailStr
from typing import Optional, List
from datetime import datetime
from .auth import CamelModel


class NhanVienDto(CamelModel):
    id: int
    ten: str
    email: EmailStr
    so_dien_thoai: Optional[str] = None
    dia_chi: Optional[str] = None
    ngay_vao_lam: datetime


class CreateNhanVienDto(CamelModel):
    ten: str = Field(min_length=1, max_length=200)
    email: EmailStr
    so_dien_thoai: Optional[str] = Field(default=None)
    dia_chi: Optional[str] = Field(default=None, max_length=500)
    ngay_vao_lam: datetime


class UpdateNhanVienDto(CamelModel):
    id: int
    ten: str = Field(min_length=1, max_length=200)
    email: EmailStr
    so_dien_thoai: Optional[str] = Field(default=None)
    dia_chi: Optional[str] = Field(default=None, max_length=500)
    ngay_vao_lam: datetime


class PagedNhanVienResult(CamelModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    items: List[NhanVienDto]
