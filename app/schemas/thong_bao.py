from typing import Optional, List
from datetime import datetime
from app.schemas.auth import CamelModel
from pydantic import Field, constr


class CreateThongBaoDto(CamelModel):
    nhan_vien_id: int = Field(..., alias='nhanVienId')
    email_nhan: constr(min_length=3, max_length=190) = Field(..., alias='emailNhan')
    ly_do: Optional[constr(max_length=500)] = Field(None, alias='lyDo')


class ThongBaoDto(CamelModel):
    id: int
    nhan_vien_id: int = Field(..., alias='nhanVienId')
    email_nhan: str = Field(..., alias='emailNhan')
    ngay_gui: datetime = Field(..., alias='ngayGui')
    ly_do: Optional[str] = Field(None, alias='lyDo')
    ngay_gui_iso: str = Field(..., alias='ngayGuiIso')
    ten_nhan_vien: Optional[str] = Field(None, alias='tenNhanVien')


class ThongBaoFilterDto(CamelModel):
    nhan_vien_id: Optional[int] = Field(None, alias='nhanVienId')
    email_nhan: Optional[str] = Field(None, alias='emailNhan')
    from_date: Optional[datetime] = Field(None, alias='from')
    to_date: Optional[datetime] = Field(None, alias='to')
    page: int = 1
    page_size: int = Field(20, alias='pageSize')


class PagedThongBaoResult(CamelModel):
    page: int
    page_size: int = Field(..., alias='pageSize')
    total_items: int = Field(..., alias='totalItems')
    total_pages: int = Field(..., alias='totalPages')
    items: List[ThongBaoDto]
