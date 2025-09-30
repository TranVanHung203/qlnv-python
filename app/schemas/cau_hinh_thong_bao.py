from typing import Optional
from pydantic import Field
from app.schemas.auth import CamelModel


class CauHinhThongBaoDto(CamelModel):
    id: int
    so_ngay_thong_bao: int
    danh_sach_nam_thong_bao: Optional[str] = None
    is_active: bool
    exclude_saturday: bool
    exclude_sunday: bool


class UpdateCauHinhThongBaoDto(CamelModel):
    id: int = Field(...)
    so_ngay_thong_bao: int = Field(..., ge=1, le=3650)
    danh_sach_nam_thong_bao: Optional[str] = None
    is_active: bool
    exclude_saturday: bool
    exclude_sunday: bool


class CreateCauHinhThongBaoDto(CamelModel):
    so_ngay_thong_bao: int = Field(60, ge=1, le=3650)
    danh_sach_nam_thong_bao: Optional[str] = None
    is_active: bool = False
    exclude_saturday: bool = True
    exclude_sunday: bool = True
