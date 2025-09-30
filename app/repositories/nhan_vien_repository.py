from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.nhan_vien import NhanVien

class NhanVienRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: NhanVien):
        # check duplicate email
        if entity.email:
            q = select(func.count()).select_from(NhanVien).where(NhanVien.email == entity.email, NhanVien.is_deleted == False)
            res = await self.session.execute(q)
            if res.scalar() > 0:
                raise Exception('Email đã tồn tại')
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, id: int):
        q = select(NhanVien).where(NhanVien.id == id, NhanVien.is_deleted == False)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def get_paged(self, page: int, page_size: int, ten: str | None = None, sdt: str | None = None):
        if page < 1: page = 1
        if page_size < 1: page_size = 8

        query = select(NhanVien).where(NhanVien.is_deleted == False)
        if ten:
            key = f"%{ten.strip().lower()}%"
            query = query.where(func.lower(NhanVien.ten).like(key))
        if sdt:
            key2 = f"%{sdt.strip().lower()}%"
            query = query.where(func.lower(NhanVien.so_dien_thoai).like(key2))

        total_q = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(total_q)
        total = total_res.scalar() or 0

        items_q = query.order_by(NhanVien.id).offset((page - 1) * page_size).limit(page_size)
        items_res = await self.session.execute(items_q)
        items = items_res.scalars().all()

        return {
            'items': items,
            'page': page,
            'page_size': page_size,
            'total_items': total,
            'total_pages': (total + page_size - 1) // page_size
        }

    async def update(self, entity: NhanVien):
        await self.session.commit()
        return entity

    async def delete(self, entity: NhanVien):
        entity.is_deleted = True
        await self.session.commit()
