from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class RefreshToken(Base):
    # Use existing table name in the database to avoid creating a duplicate
    # table. Your DB already has a table named `refreshtokens`.
    __tablename__ = 'refreshtokens'
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    # MySQL/MariaDB with utf8mb4 uses up to 4 bytes per character. To avoid
    # 'Specified key was too long; max key length is 767 bytes' when a column
    # is part of a primary key or indexed, keep the length <= 191 characters
    # (191 * 4 = 764 bytes) which fits within the 767-byte limit.
    token = Column("Token", String(191), primary_key=True)
    # use_alter=True tells SQLAlchemy to emit the FK with ALTER TABLE after
    # both tables have been created which helps avoid ordering/charset issues
    # when using create_all. Also name the FK for clarity.
    user_id = Column("UserId", String(36), ForeignKey('users.Id', name='fk_refresh_user_id', use_alter=True), nullable=False)
    expires = Column("Expires", DateTime, nullable=False)
    # created_at column removed to match existing DB schema
    is_revoked = Column("IsRevoked", Boolean, default=False)

    user = relationship('User', back_populates='refresh_tokens')
