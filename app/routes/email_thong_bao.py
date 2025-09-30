from fastapi import APIRouter, Depends, HTTPException
from app.schemas.email_thong_bao import CreateEmailThongBaoDto, UpdateEmailThongBaoDto, EmailThongBaoDto, PagedEmailThongBaoResult
from app.schemas import PagedResult
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.email_thong_bao_service import EmailThongBaoService
from app.deps import get_current_user

router = APIRouter()

@router.get('/', response_model=PagedEmailThongBaoResult, dependencies=[Depends(get_current_user)])
async def get_all(page: int = 1, page_size: int = 8, email: str | None = None, session: AsyncSession = Depends(get_db)):
    svc = EmailThongBaoService(session)
    res = await svc.get_paged(page, page_size, email)
    # service returns a PagedEmailThongBaoResult; return it directly
    return res

@router.get('/{id}', response_model=EmailThongBaoDto,dependencies=[Depends(get_current_user)])
async def get_by_id(id: int, session: AsyncSession = Depends(get_db)):
    svc = EmailThongBaoService(session)
    res = await svc.get_by_id(id)
    if not res:
        raise HTTPException(status_code=404, detail='Không tìm thấy email thông báo')
    return res

@router.post('/', response_model=EmailThongBaoDto,dependencies=[Depends(get_current_user)])
async def create(dto: CreateEmailThongBaoDto, session: AsyncSession = Depends(get_db),user=Depends(get_current_user)):
    svc = EmailThongBaoService(session)
    try:
        return await svc.create(dto)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.put('/{id}', response_model=EmailThongBaoDto,dependencies=[Depends(get_current_user)])
async def update(id: int, dto: UpdateEmailThongBaoDto, session: AsyncSession = Depends(get_db)):
    if id != dto.id:
        raise HTTPException(status_code=400, detail='Id không khớp')
    svc = EmailThongBaoService(session)
    try:
        return await svc.update(dto)
    except KeyError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.delete('/{id}', status_code=204,dependencies=[Depends(get_current_user)])
async def delete(id: int, session: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    svc = EmailThongBaoService(session)
    try:
        await svc.delete(id)
    except KeyError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
