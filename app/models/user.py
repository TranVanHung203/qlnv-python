import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = 'users'
    # Ensure MySQL uses a consistent engine and charset so FKs match exactly
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id = Column("Id", String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column("Username", String(50), nullable=False, unique=True)
    email = Column("Email", String(100), nullable=False, unique=True)
    password_hash = Column("PasswordHash", String(200), nullable=False)
    full_name = Column("FullName", String(100), nullable=True)
    is_deleted = Column("IsDeleted", Boolean, default=False)
    email_confirmed = Column("EmailConfirmed", Boolean, default=False)
    email_confirmation_token = Column("EmailConfirmationToken", String(200), nullable=True)
    email_confirmation_expiry = Column("EmailConfirmationExpiry", DateTime, nullable=True)
    role = Column("Role", String(50), default='Assistant')

    refresh_tokens = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')
