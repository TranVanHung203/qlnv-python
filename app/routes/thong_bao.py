from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.thong_bao import ThongBaoFilterDto, PagedThongBaoResult
from app.services.thong_bao_service import ThongBaoService
from app.db import get_db
from app.deps import get_current_user


router = APIRouter()


@router.get('/', response_model=PagedThongBaoResult, dependencies=[Depends(get_current_user)])
async def get_all(filter: ThongBaoFilterDto = Depends(), session: AsyncSession = Depends(get_db)):
    svc = ThongBaoService(session)
    res = await svc.get_paged(filter.page, filter.page_size, filter.nhan_vien_id, filter.email_nhan, filter.from_date, filter.to_date)
    return res
