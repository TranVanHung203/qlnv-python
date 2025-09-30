from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base


class NgayLe(Base):
    __tablename__ = 'ngayle'
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    ten_ngay_le = Column('TenNgayLe', String(190), nullable=False)
    ngay_bat_dau = Column('NgayBatDau', DateTime, nullable=False)
    ngay_ket_thuc = Column('NgayKetThuc', DateTime, nullable=False)
