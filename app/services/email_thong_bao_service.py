from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.email_thong_bao_repository import EmailThongBaoRepository
from app.schemas.email_thong_bao import CreateEmailThongBaoDto, EmailThongBaoDto, PagedEmailThongBaoResult, UpdateEmailThongBaoDto
from app.models.email_thong_bao import EmailThongBao

class EmailThongBaoService:
    def __init__(self, session: AsyncSession):
        self.repo = EmailThongBaoRepository(session)

    async def create(self, dto: CreateEmailThongBaoDto):
        entity = EmailThongBao(email=dto.email, name=dto.name)
        created = await self.repo.create(entity)
        return EmailThongBaoDto(id=created.id, email=created.email, name=created.name)

    async def get_by_id(self, id: int):
        e = await self.repo.get_by_id(id)
        if not e: return None
        return EmailThongBaoDto(id=e.id, email=e.email, name=e.name)

    async def get_paged(self, page: int, page_size: int, email: str | None = None):
        res = await self.repo.get_paged(page, page_size, email)
        items = [EmailThongBaoDto(id=i.id, email=i.email, name=i.name) for i in res['items']]
        return PagedEmailThongBaoResult(page=res['page'], page_size=res['page_size'], total_items=res['total_items'], total_pages=res['total_pages'], items=items)

    async def update(self, dto: UpdateEmailThongBaoDto):
        entity = await self.repo.get_by_id(dto.id)
        if not entity:
            raise KeyError('Không tìm thấy Email thông báo')
        entity.email = dto.email
        entity.name = dto.name
        updated = await self.repo.update(entity)
        return EmailThongBaoDto(id=updated.id, email=updated.email, name=updated.name)

    async def delete(self, id: int):
        entity = await self.repo.get_by_id(id)
        if not entity:
            raise KeyError('Không tìm thấy Email thông báo')
        await self.repo.delete(entity)
