from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class ThongBao(Base):
    __tablename__ = 'thongbao'
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    nhan_vien_id = Column('NhanVienId', Integer, ForeignKey('nhanvien.Id'), nullable=False)
    email_nhan = Column('EmailNhan', String(190), nullable=False)
    ngay_gui = Column('NgayGui', DateTime, nullable=False, default=datetime.utcnow)
    ly_do = Column('LyDo', String(500), nullable=True)

    # relationship
    nhan_vien = relationship('NhanVien')
