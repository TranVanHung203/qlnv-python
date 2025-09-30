from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import CreateUserDto, UpdateUserDto, UserDto, PagedResult
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService
from typing import List
from app.deps import get_current_user, require_role

router = APIRouter()

@router.post('/', response_model=UserDto, dependencies=[Depends(require_role('Admin'))])
async def create_user(dto: CreateUserDto, session: AsyncSession = Depends(get_db)):
    svc = UserService(session)
    try:
        created = await svc.create_user(dto)
        return UserDto(id=created.id, username=created.username, email=created.email, full_name=created.full_name or "", role=created.role)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get('/', response_model=PagedResult, dependencies=[Depends(get_current_user)])
async def get_all(page: int = 1, q: str | None = None, session: AsyncSession = Depends(get_db)):
    svc = UserService(session)
    res = await svc.get_paged(page, 10, q)
    items = [UserDto(id=u.id, username=u.username, email=u.email, full_name=u.full_name or "", role=u.role) for u in res['items']]
    return PagedResult(page=res['page'], page_size=res['page_size'], total_items=res['total_items'], total_pages=res['total_pages'], items=items)

@router.get('/{id}', response_model=UserDto, dependencies=[Depends(get_current_user)])
async def get_by_id(id: str, session: AsyncSession = Depends(get_db)):
    svc = UserService(session)
    u = await svc.get_by_id(id)
    if not u:
        raise HTTPException(status_code=404)
    return UserDto(id=u.id, username=u.username, email=u.email, full_name=u.full_name or "", role=u.role)

@router.put('/{id}', response_model=UserDto, dependencies=[Depends(require_role('Admin'))])
async def update_user(id: str, dto: UpdateUserDto, session: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    svc = UserService(session)
    try:
        current_role = current_user.get('role') or current_user.get('http://schemas.microsoft.com/ws/2008/06/identity/claims/role')
        updated = await svc.update(id, dto, current_user_role=current_role)
        return UserDto(id=updated.id, username=updated.username, email=updated.email, full_name=updated.full_name, role=updated.role)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.delete('/{id}', status_code=204, dependencies=[Depends(require_role('Admin'))])
async def delete_user(id: str, session: AsyncSession = Depends(get_db)):
    svc = UserService(session)
    try:
        await svc.delete(id)
        return
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
