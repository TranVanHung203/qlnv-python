from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.schemas import LoginDto, AuthResponseDto, RefreshTokenRequestDto, ForgotPasswordDto, ResetPasswordDto
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from app.utils import send_email

router = APIRouter()


@router.post('/login', response_model=AuthResponseDto)
async def login(dto: LoginDto, session: AsyncSession = Depends(get_db)):
    svc = AuthService(session)
    try:
        return await svc.login(dto.username, dto.password)
    except Exception as ex:
        raise HTTPException(status_code=401, detail=str(ex))


@router.post('/refresh', response_model=AuthResponseDto)
async def refresh(dto: RefreshTokenRequestDto, session: AsyncSession = Depends(get_db)):
    svc = AuthService(session)
    try:
        return await svc.refresh_token(dto.refresh_token)
    except Exception as ex:
        raise HTTPException(status_code=401, detail=str(ex))


@router.post('/forgot-password')
async def forgot(dto: ForgotPasswordDto, background: BackgroundTasks, session: AsyncSession = Depends(get_db)):
    svc = AuthService(session)
    email_params = await svc.forgot_password(dto.email)
    if email_params:
        # schedule sending the email in background
        background.add_task(send_email, email_params['to'], email_params['subject'], email_params['body'])
    return {"message": "Nếu email tồn tại, link reset sẽ được gửi"}


@router.post('/reset-password')
async def reset(dto: ResetPasswordDto, session: AsyncSession = Depends(get_db)):
    svc = AuthService(session)
    try:
        await svc.reset_password(dto.email, dto.token, dto.new_password)
        return {"message": "Đổi mật khẩu thành công"}
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
