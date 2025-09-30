from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str):
        q = select(User).where(User.username == username, User.is_deleted == False)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def get_by_email(self, email: str):
        q = select(User).where(User.email == email, User.is_deleted == False)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def get_by_id(self, id: str):
        q = select(User).where(User.id == id, User.is_deleted == False)
        res = await self.session.execute(q)
        user = res.scalars().first()
        if user and user.full_name is None:
            user.full_name = ""
        return user

    async def create(self, user: User):
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User):
        await self.session.commit()
        return user

    async def delete(self, user: User):
        user.is_deleted = True
        await self.session.commit()

    async def get_paged(self, page: int, page_size: int, qstr: str | None = None):
        if page < 1: page = 1
        if page_size < 1: page_size = 10

        query = select(User).where(User.is_deleted == False)
        if qstr:
            key = f"%{qstr.lower()}%"
            query = query.where(func.lower(User.username).like(key) | func.lower(User.email).like(key))

        total_q = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(total_q)
        total = total_res.scalar() or 0

        items_q = query.order_by(User.username).offset((page - 1) * page_size).limit(page_size)
        items_res = await self.session.execute(items_q)
        items = items_res.scalars().all()

        # normalize null full_name to empty string for consumers
        for u in items:
            if u.full_name is None:
                u.full_name = ""

        return {
            'items': items,
            'page': page,
            'page_size': page_size,
            'total_items': total,
            'total_pages': (total + page_size - 1) // page_size
        }
