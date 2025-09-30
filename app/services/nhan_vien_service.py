from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.nhan_vien_repository import NhanVienRepository
from app.schemas.nhan_vien import CreateNhanVienDto, NhanVienDto, PagedNhanVienResult, UpdateNhanVienDto
from app.models.nhan_vien import NhanVien

class NhanVienService:
    def __init__(self, session: AsyncSession):
        self.repo = NhanVienRepository(session)

    async def create(self, dto: CreateNhanVienDto):
        entity = NhanVien(ten=dto.ten, email=dto.email, so_dien_thoai=dto.so_dien_thoai, dia_chi=dto.dia_chi, ngay_vao_lam=dto.ngay_vao_lam)
        created = await self.repo.create(entity)
        return NhanVienDto(id=created.id, ten=created.ten, email=created.email, so_dien_thoai=created.so_dien_thoai, dia_chi=created.dia_chi, ngay_vao_lam=created.ngay_vao_lam)

    async def get_by_id(self, id: int):
        e = await self.repo.get_by_id(id)
        if not e: return None
        return NhanVienDto(id=e.id, ten=e.ten, email=e.email, so_dien_thoai=e.so_dien_thoai, dia_chi=e.dia_chi, ngay_vao_lam=e.ngay_vao_lam)

    async def get_paged(self, page: int, page_size: int, ten: str | None = None, sdt: str | None = None):
        res = await self.repo.get_paged(page, page_size, ten, sdt)
        items = [NhanVienDto(id=i.id, ten=i.ten, email=i.email, so_dien_thoai=i.so_dien_thoai, dia_chi=i.dia_chi, ngay_vao_lam=i.ngay_vao_lam) for i in res['items']]
        return PagedNhanVienResult(page=res['page'], page_size=res['page_size'], total_items=res['total_items'], total_pages=res['total_pages'], items=items)

    async def update(self, dto: UpdateNhanVienDto):
        entity = await self.repo.get_by_id(dto.id)
        if not entity:
            raise KeyError('Không tìm thấy nhân viên')
        entity.ten = dto.ten
        entity.email = dto.email
        entity.so_dien_thoai = dto.so_dien_thoai
        entity.dia_chi = dto.dia_chi
        entity.ngay_vao_lam = dto.ngay_vao_lam
        updated = await self.repo.update(entity)
        return NhanVienDto(id=updated.id, ten=updated.ten, email=updated.email, so_dien_thoai=updated.so_dien_thoai, dia_chi=updated.dia_chi, ngay_vao_lam=updated.ngay_vao_lam)

    async def delete(self, id: int):
        e = await self.repo.get_by_id(id)
        if not e:
            raise KeyError('Không tìm thấy nhân viên')
        await self.repo.delete(e)
