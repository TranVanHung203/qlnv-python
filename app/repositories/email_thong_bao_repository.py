from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.email_thong_bao import EmailThongBao

class EmailThongBaoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: EmailThongBao):
        # check duplicate email
        if entity.email:
            q = select(func.count()).select_from(EmailThongBao).where(func.lower(EmailThongBao.email) == entity.email.lower())
            res = await self.session.execute(q)
            if res.scalar() > 0:
                raise Exception('Email đã tồn tại.')
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, id: int):
        q = select(EmailThongBao).where(EmailThongBao.id == id)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def get_paged(self, page: int, page_size: int, email: str | None = None):
        if page < 1: page = 1
        if page_size < 1: page_size = 8

        query = select(EmailThongBao)
        if email:
            key = f"%{email.strip().lower()}%"
            query = query.where(func.lower(EmailThongBao.email).like(key) | (EmailThongBao.name != None and func.lower(EmailThongBao.name).like(key)))

        total_q = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(total_q)
        total = total_res.scalar() or 0

        items_q = query.order_by(EmailThongBao.id).offset((page - 1) * page_size).limit(page_size)
        items_res = await self.session.execute(items_q)
        items = items_res.scalars().all()

        return {
            'items': items,
            'page': page,
            'page_size': page_size,
            'total_items': total,
            'total_pages': (total + page_size - 1) // page_size
        }

    async def update(self, entity: EmailThongBao):
        # check duplicate email
        if entity.email:
            q = select(func.count()).select_from(EmailThongBao).where(EmailThongBao.id != entity.id, func.lower(EmailThongBao.email) == entity.email.lower())
            res = await self.session.execute(q)
            if res.scalar() > 0:
                raise Exception('Email đã tồn tại.')
        self.session.add(entity)
        await self.session.commit()
        return entity

    async def delete(self, entity: EmailThongBao):
        await self.session.delete(entity)
        await self.session.commit()
