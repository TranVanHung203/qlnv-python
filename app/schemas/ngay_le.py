from datetime import datetime
from pydantic import Field
from typing import Optional, List
from .auth import CamelModel


class CreateNgayLeDto(CamelModel):
    ten_ngay_le: str = Field(..., min_length=1, max_length=100)
    ngay_bat_dau: datetime
    ngay_ket_thuc: datetime


class UpdateNgayLeDto(CreateNgayLeDto):
    id: int


class NgayLeDto(CamelModel):
    id: int
    ten_ngay_le: str
    ngay_bat_dau: datetime
    ngay_ket_thuc: datetime


class PagedNgayLeResult(CamelModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    items: List[NgayLeDto]
