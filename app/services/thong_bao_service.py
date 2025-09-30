from app.repositories.thong_bao_repository import ThongBaoRepository
from app.schemas.thong_bao import CreateThongBaoDto, ThongBaoDto, PagedThongBaoResult
from app.models.thong_bao import ThongBao
from datetime import datetime


class ThongBaoService:
    def __init__(self, session):
        self.repo = ThongBaoRepository(session)

    async def create(self, dto: CreateThongBaoDto):
        entity = ThongBao(
            nhan_vien_id=dto.nhan_vien_id,
            email_nhan=dto.email_nhan,
            ly_do=dto.ly_do,
            ngay_gui=datetime.utcnow()
        )

        created = await self.repo.create(entity)

        return ThongBaoDto(
            id=created.id,
            nhan_vien_id=created.nhan_vien_id,
            email_nhan=created.email_nhan,
            ngay_gui=created.ngay_gui,
            ly_do=created.ly_do,
            ngay_gui_iso=created.ngay_gui.replace(tzinfo=None).isoformat() + 'Z'
        )

    async def get_paged(self, page: int, page_size: int, nhan_vien_id: int | None = None, email_nhan: str | None = None, from_date=None, to_date=None):
        res = await self.repo.get_paged(page, page_size, nhan_vien_id, email_nhan, from_date, to_date)

        items = []
        for i in res['items']:
            items.append(ThongBaoDto(
                id=i.id,
                nhan_vien_id=i.nhan_vien_id,
                email_nhan=i.email_nhan,
                ngay_gui=i.ngay_gui,
                ly_do=i.ly_do,
                ngay_gui_iso=(i.ngay_gui.isoformat() if i.ngay_gui.tzinfo else i.ngay_gui.replace(tzinfo=None).isoformat() + 'Z'),
                ten_nhan_vien=(getattr(i, 'nhan_vien').ten if getattr(i, 'nhan_vien', None) else None)
            ))

        return PagedThongBaoResult(
            page=res['page'],
            page_size=res['page_size'],
            total_items=res['total_items'],
            total_pages=res['total_pages'],
            items=items
        )
