from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import RefreshToken
from datetime import datetime, timedelta
import secrets

class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(self, user_id: str, days: int = 30):
        token = secrets.token_urlsafe(64)
        expires = datetime.utcnow() + timedelta(days=days)
        rt = RefreshToken(token=token, user_id=user_id, expires=expires)
        self.session.add(rt)
        await self.session.commit()
        return rt

    async def get_by_token(self, token: str):
        q = select(RefreshToken).where(RefreshToken.token == token)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def rotate_refresh_token(self, token_entity: RefreshToken):
        token_entity.is_revoked = True
        await self.session.commit()
        return await self.create_refresh_token(token_entity.user_id)
