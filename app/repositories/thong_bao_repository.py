from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.thong_bao import ThongBao


class ThongBaoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: ThongBao):
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def exists_for_nhan_vien_on_date(self, nhan_vien_id: int, date_utc):
        d = date_utc.date()
        q = select(func.count()).select_from(ThongBao).where(ThongBao.nhan_vien_id == nhan_vien_id)
        # note: compare date portion in app layer when filtering down below
        # We'll perform a simple query and check in DB if date matches via SQL functions in other repos; keep simple here
        q = q.where(func.date(ThongBao.ngay_gui) == d)
        res = await self.session.execute(q)
        return res.scalar_one() > 0

    async def exists_for_nhan_vien_with_reason(self, nhan_vien_id: int, reason: str, email_nhan: str):
        if not reason or not email_nhan:
            return False
        email = email_nhan.strip().lower()
        q = select(func.count()).select_from(ThongBao).where(
            ThongBao.nhan_vien_id == nhan_vien_id,
            ThongBao.ly_do == reason,
            func.lower(ThongBao.email_nhan) == email
        )
        res = await self.session.execute(q)
        return res.scalar_one() > 0

    async def get_paged(self, page: int, page_size: int, nhan_vien_id: Optional[int] = None, email_nhan: Optional[str] = None, from_date=None, to_date=None):
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10

        # eagerly load nhan_vien to avoid lazy loading in async context
        query = select(ThongBao).options(selectinload(ThongBao.nhan_vien)).order_by(ThongBao.ngay_gui.desc())

        if nhan_vien_id:
            query = query.where(ThongBao.nhan_vien_id == nhan_vien_id)
        if email_nhan:
            key = f"%{email_nhan.strip().lower()}%"
            query = query.where(func.lower(ThongBao.email_nhan).like(key))
        if from_date:
            query = query.where(func.date(ThongBao.ngay_gui) >= from_date.date())
        if to_date:
            query = query.where(func.date(ThongBao.ngay_gui) <= to_date.date())

        total_q = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(total_q)
        total = total_res.scalar_one()

        items_q = query.offset((page - 1) * page_size).limit(page_size)
        items_res = await self.session.execute(items_q)
        items = items_res.scalars().all()

        return {
            'items': items,
            'page': page,
            'page_size': page_size,
            'total_items': total,
            'total_pages': (int((total + page_size - 1) / page_size))
        }
