import uuid
import os

from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings
from app.repositories import UserRepository, RefreshTokenRepository
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from app.schemas.auth import AuthResponseDto

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.refresh_repo = RefreshTokenRepository(session)

    async def login(self, username: str, password: str):
        user = await self.user_repo.get_by_username(username)
        if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            raise Exception("Sai tài khoản hoặc mật khẩu")

        token, exp = self._generate_jwt(user)
        refresh = await self.refresh_repo.create_refresh_token(user.id)
        # return explicit camelCase keys to match response_model alias expectations
        return {"token": token, "refreshToken": refresh.token, "expiration": exp}

    async def refresh_token(self, refresh_token: str):
        token_entity = await self.refresh_repo.get_by_token(refresh_token)
        if not token_entity or token_entity.is_revoked or token_entity.expires < datetime.utcnow():
            raise Exception("Refresh token không hợp lệ")

        user = await self.user_repo.get_by_id(token_entity.user_id)
        if not user: raise Exception("User không tồn tại")

        token, exp = self._generate_jwt(user)
        new_refresh = await self.refresh_repo.rotate_refresh_token(token_entity)
        return {"token": token, "refreshToken": new_refresh.token, "expiration": exp}

    async def forgot_password(self, email: str):
        user = await self.user_repo.get_by_email(email)
        if not user: return
        user.email_confirmation_token = str(uuid.uuid4())
        user.email_confirmation_expiry = datetime.utcnow() + timedelta(hours=1)
        await self.user_repo.update(user)

        # Build a reset link — frontend should handle the route and POST back to /reset-password
        reset_link = f"https://your-frontend.example.com/reset-password?email={user.email}&token={user.email_confirmation_token}"
        subject = "Yêu cầu đặt lại mật khẩu"
        body = f"Xin chào {user.full_name or user.username},\n\n" \
               f"Bạn hoặc ai đó đã yêu cầu đặt lại mật khẩu cho tài khoản này.\n" \
               f"Vui lòng sử dụng liên kết sau để đặt lại mật khẩu. Liên kết có hiệu lực trong 1 giờ:\n\n{reset_link}\n\n" \
               "Nếu bạn không yêu cầu, vui lòng bỏ qua email này.\n"

        # Return email params so caller (route) can send it via BackgroundTasks
        return {"to": user.email, "subject": subject, "body": body}

    async def reset_password(self, email: str, token: str, new_password: str):
        user = await self.user_repo.get_by_email(email)
        if not user: raise Exception("User không tồn tại")
        if user.email_confirmation_token != token or user.email_confirmation_expiry < datetime.utcnow():
            raise Exception("Token không hợp lệ hoặc đã hết hạn")

        user.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        user.email_confirmation_token = None
        user.email_confirmation_expiry = None
        await self.user_repo.update(user)

    def _generate_jwt(self, user: User):
        secret = settings.secret_key
        expires_minutes = settings.access_token_expire_minutes
       
        # Use timezone-aware UTC datetime so .timestamp() is unambiguous
        exp = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        # Build payload with issuer/audience and the MS role claim URI to match legacy tokens
        payload = {
            "sub": user.id,
            "unique_name": user.username,
            "fullname": user.full_name or "",
            # include both a short 'role' and the MS role claim for compatibility
            "role": user.role or "Assistant",
            "http://schemas.microsoft.com/ws/2008/06/identity/claims/role": user.role or "Assistant",
            "exp": int(exp.timestamp()),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return token, exp
