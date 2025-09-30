from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.db import Base


class NhanVien(Base):
    __tablename__ = 'nhanvien'
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    ten = Column('Ten', String(190), nullable=False)
    email = Column('Email', String(190), nullable=False, unique=True)
    so_dien_thoai = Column('SoDienThoai', String(50), nullable=True)
    dia_chi = Column('DiaChi', String(190), nullable=True)
    ngay_vao_lam = Column('NgayVaoLam', DateTime, nullable=False)
    is_deleted = Column('IsDeleted', Boolean, default=False)
