from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base


class CauHinhThongBao(Base):
    __tablename__ = 'cauhinhthongbao'
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    so_ngay_thong_bao = Column('SoNgayThongBao', Integer, nullable=False, default=60)
    danh_sach_nam_thong_bao = Column('DanhSachNamThongBao', String(200), nullable=True)
    is_active = Column('IsActive', Boolean, nullable=False, default=False)
    exclude_saturday = Column('ExcludeSaturday', Boolean, nullable=False, default=True)
    exclude_sunday = Column('ExcludeSunday', Boolean, nullable=False, default=True)
