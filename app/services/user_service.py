from app.repositories import UserRepository
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def create_user(self, dto):
        existing = await self.user_repo.get_by_username(dto.username)
        if existing: raise Exception("Username already exists")
        existing = await self.user_repo.get_by_email(dto.email)
        if existing: raise Exception("Email already exists")

        user = User(
            username=dto.username,
            email=dto.email,
            password_hash=bcrypt.hashpw(dto.password.encode(), bcrypt.gensalt()).decode(),
            full_name=dto.full_name or "",
            role=dto.role or "Assistant"
        )
        created = await self.user_repo.create(user)
        return created

    async def get_paged(self, page, page_size, q):
        return await self.user_repo.get_paged(page, page_size, q)

    async def get_by_id(self, id):
        return await self.user_repo.get_by_id(id)

    async def update(self, id: str, dto, current_user_role: str):
        existing = await self.user_repo.get_by_id(id)
        if not existing: raise Exception("User not found")

        if dto.role and dto.role != existing.role:
            if current_user_role != "Admin":
                raise Exception("Only Admin can change role")
            # assign the new role when allowed
            existing.role = dto.role

        if dto.full_name: existing.full_name = dto.full_name
        if dto.email: existing.email = dto.email

        await self.user_repo.update(existing)
        return existing

    async def delete(self, id):
        existing = await self.user_repo.get_by_id(id)
        if not existing: raise Exception("User not found")
        await self.user_repo.delete(existing)
