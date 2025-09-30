from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ngay_le import CreateNgayLeDto, UpdateNgayLeDto, NgayLeDto, PagedNgayLeResult
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ngay_le_service import NgayLeService
from app.deps import get_current_user

router = APIRouter()


@router.post('/', response_model=NgayLeDto, dependencies=[Depends(get_current_user)])
async def create(dto: CreateNgayLeDto, session: AsyncSession = Depends(get_db)):
    svc = NgayLeService(session)
    try:
        return await svc.create(dto)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get('/{id}', response_model=NgayLeDto, dependencies=[Depends(get_current_user)])
async def get_by_id(id: int, session: AsyncSession = Depends(get_db)):
    svc = NgayLeService(session)
    res = await svc.get_by_id(id)
    if not res:
        raise HTTPException(status_code=404, detail='Không tìm thấy ngày lễ')
    return res


@router.get('/', response_model=PagedNgayLeResult, dependencies=[Depends(get_current_user)])
async def get_all(page: int = 1, ten: str | None = None, session: AsyncSession = Depends(get_db)):
    svc = NgayLeService(session)
    return await svc.get_paged(page, 8, ten)


@router.put('/{id}', response_model=NgayLeDto, dependencies=[Depends(get_current_user)])
async def update(id: int, dto: UpdateNgayLeDto, session: AsyncSession = Depends(get_db)):
    if id != dto.id:
        raise HTTPException(status_code=400, detail='Id không khớp')
    svc = NgayLeService(session)
    try:
        return await svc.update(dto)
    except KeyError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.delete('/{id}', status_code=204, dependencies=[Depends(get_current_user)])
async def delete(id: int, session: AsyncSession = Depends(get_db)):
    svc = NgayLeService(session)
    try:
        await svc.delete(id)
    except KeyError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
