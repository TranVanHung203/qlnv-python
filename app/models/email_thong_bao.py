from sqlalchemy import Column, Integer, String
from app.db import Base


class EmailThongBao(Base):
    __tablename__ = 'emailthongbao'
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    email = Column('Email', String(190), nullable=False, unique=True)
    name = Column('Name', String(190), nullable=True)
  
