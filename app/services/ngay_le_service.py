from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.ngay_le_repository import NgayLeRepository
from app.schemas.ngay_le import CreateNgayLeDto, NgayLeDto, PagedNgayLeResult, UpdateNgayLeDto
from app.models.ngay_le import NgayLe


class NgayLeService:
    def __init__(self, session: AsyncSession):
        self.repo = NgayLeRepository(session)

    async def create(self, dto: CreateNgayLeDto):
        entity = NgayLe(ten_ngay_le=dto.ten_ngay_le, ngay_bat_dau=dto.ngay_bat_dau, ngay_ket_thuc=dto.ngay_ket_thuc)
        created = await self.repo.create(entity)
        return NgayLeDto(id=created.id, ten_ngay_le=created.ten_ngay_le, ngay_bat_dau=created.ngay_bat_dau, ngay_ket_thuc=created.ngay_ket_thuc)

    async def get_by_id(self, id: int):
        e = await self.repo.get_by_id(id)
        if not e: return None
        return NgayLeDto(id=e.id, ten_ngay_le=e.ten_ngay_le, ngay_bat_dau=e.ngay_bat_dau, ngay_ket_thuc=e.ngay_ket_thuc)

    async def get_paged(self, page: int, page_size: int, ten: str | None = None):
        res = await self.repo.get_paged(page, page_size, ten)
        items = [NgayLeDto(id=i.id, ten_ngay_le=i.ten_ngay_le, ngay_bat_dau=i.ngay_bat_dau, ngay_ket_thuc=i.ngay_ket_thuc) for i in res['items']]
        return PagedNgayLeResult(page=res['page'], page_size=res['page_size'], total_items=res['total_items'], total_pages=res['total_pages'], items=items)

    async def update(self, dto: UpdateNgayLeDto):
        entity = await self.repo.get_by_id(dto.id)
        if not entity:
            raise KeyError('Không tìm thấy ngày lễ.')
        entity.ten_ngay_le = dto.ten_ngay_le
        entity.ngay_bat_dau = dto.ngay_bat_dau
        entity.ngay_ket_thuc = dto.ngay_ket_thuc
        updated = await self.repo.update(entity)
        return NgayLeDto(id=updated.id, ten_ngay_le=updated.ten_ngay_le, ngay_bat_dau=updated.ngay_bat_dau, ngay_ket_thuc=updated.ngay_ket_thuc)

    async def delete(self, id: int):
        e = await self.repo.get_by_id(id)
        if not e:
            raise KeyError('Không tìm thấy ngày lễ.')
        await self.repo.delete(e)
