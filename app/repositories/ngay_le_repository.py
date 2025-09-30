from sqlalchemy import select, func
from app.models.ngay_le import NgayLe
from sqlalchemy.ext.asyncio import AsyncSession


class NgayLeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: NgayLe):
        # check duplicate TenNgayLe
        if entity.ten_ngay_le:
            q = select(func.count()).select_from(NgayLe).where(func.lower(NgayLe.ten_ngay_le) == entity.ten_ngay_le.lower())
            res = await self.session.execute(q)
            if res.scalar() > 0:
                raise Exception('Tên ngày lễ đã tồn tại.')

        if entity.ngay_ket_thuc < entity.ngay_bat_dau:
            raise Exception('Ngày kết thúc phải >= ngày bắt đầu.')

        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, id: int):
        q = select(NgayLe).where(NgayLe.id == id)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def get_paged(self, page: int, page_size: int, ten: str | None = None):
        if page < 1: page = 1
        if page_size < 1: page_size = 8

        query = select(NgayLe)
        if ten and ten.strip():
            key = f"%{ten.strip().lower()}%"
            query = query.where(func.lower(NgayLe.ten_ngay_le).like(key))

        total_q = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(total_q)
        total = total_res.scalar() or 0

        items_q = query.order_by(NgayLe.id).offset((page - 1) * page_size).limit(page_size)
        items_res = await self.session.execute(items_q)
        items = items_res.scalars().all()

        return {
            'items': items,
            'page': page,
            'page_size': page_size,
            'total_items': total,
            'total_pages': (total + page_size - 1) // page_size
        }

    async def update(self, entity: NgayLe):
        await self.session.commit()
        return entity

    async def delete(self, entity: NgayLe):
        await self.session.delete(entity)
        await self.session.commit()
