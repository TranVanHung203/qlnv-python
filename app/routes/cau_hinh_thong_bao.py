from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.cau_hinh_thong_bao_service import CauHinhThongBaoService
from app.schemas.cau_hinh_thong_bao import CauHinhThongBaoDto, CreateCauHinhThongBaoDto, UpdateCauHinhThongBaoDto
from app.deps import get_current_user

router = APIRouter()


@router.get('/active', response_model=CauHinhThongBaoDto, dependencies=[Depends(get_current_user)])
async def get_active(session: AsyncSession = Depends(get_db)):
    svc = CauHinhThongBaoService(session)
    res = await svc.get_active_only_async()
    if res is None:
        raise HTTPException(status_code=404, detail="No explicitly active configuration found")
    return res


@router.get('/all', response_model=list[CauHinhThongBaoDto], dependencies=[Depends(get_current_user)])
async def get_all(session: AsyncSession = Depends(get_db)):
    svc = CauHinhThongBaoService(session)
    return await svc.get_all_configs_async()


@router.get('/{id}', response_model=CauHinhThongBaoDto, dependencies=[Depends(get_current_user)])
async def get_by_id(id: int, session: AsyncSession = Depends(get_db)):
    svc = CauHinhThongBaoService(session)
    res = await svc.get_config_by_id_async(id)
    if res is None:
        raise HTTPException(status_code=404)
    return res


@router.post('/{id}/activate', response_model=CauHinhThongBaoDto, dependencies=[Depends(get_current_user)])
async def activate(id: int, session: AsyncSession = Depends(get_db)):
    svc = CauHinhThongBaoService(session)
    res = await svc.get_config_by_id_async(id)
    if res is None:
        raise HTTPException(status_code=404)
    # Activation handled in service/repo
    cfg = await svc.repo.get_by_id_async(id)
    cfg.is_active = True
    updated = await svc.repo.update_async(cfg)
    return CauHinhThongBaoDto(id=updated.id, so_ngay_thong_bao=updated.so_ngay_thong_bao, danh_sach_nam_thong_bao=updated.danh_sach_nam_thong_bao, is_active=updated.is_active, exclude_saturday=updated.exclude_saturday, exclude_sunday=updated.exclude_sunday)


@router.put('/', response_model=CauHinhThongBaoDto, dependencies=[Depends(get_current_user)])
async def update(dto: UpdateCauHinhThongBaoDto, session: AsyncSession = Depends(get_db)):
    svc = CauHinhThongBaoService(session)
    return await svc.update_config_async(dto)


@router.post('/', response_model=CauHinhThongBaoDto, dependencies=[Depends(get_current_user)])
async def create(dto: CreateCauHinhThongBaoDto, session: AsyncSession = Depends(get_db)):
    svc = CauHinhThongBaoService(session)
    return await svc.create_config_async(dto)


@router.post('/run', dependencies=[Depends(get_current_user)])
async def run(session: AsyncSession = Depends(get_db)):
    svc = CauHinhThongBaoService(session)
    sent = await svc.run_check_and_send()
    return {"sent": sent}


@router.delete('/{id}', dependencies=[Depends(get_current_user)])
async def delete(id: int, session: AsyncSession = Depends(get_db)):
    svc = CauHinhThongBaoService(session)
    await svc.delete_config_async(id)
    return None
