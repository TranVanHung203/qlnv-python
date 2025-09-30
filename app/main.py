from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import asyncio
from datetime import datetime, timedelta
from app.deps import get_current_user
from app.routes import auth, users
from app.routes import email_thong_bao
from app.routes import nhan_vien
from app.routes import ngay_le
from app.routes import thong_bao
from app.routes import cau_hinh_thong_bao
from app.config import settings
from app.db import init_db
from app.db import AsyncSessionLocal
import asyncio
from app.services.cau_hinh_thong_bao_service import CauHinhThongBaoService
from app.repositories.cau_hinh_thong_bao_repository import CauHinhThongBaoRepository
import logging
from app.error_handlers import register_error_handlers

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


app = FastAPI(
    title="qlnv-fastapi",
    swagger_ui_parameters={"persistAuthorization": True},
    
)

# register centralized error handlers
register_error_handlers(app)


# CORS cho Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.1.140:8080",  # Angular chạy trong mạng LAN
        "http://localhost:4200",      # Angular dev local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Chỉ bật redirect HTTPS nếu chạy production
if not settings.debug:
    app.add_middleware(HTTPSRedirectMiddleware)


# (validation and other exception handlers are registered via app.error_handlers.register_error_handlers)


# Init database khi app start
@app.on_event("startup")
async def startup():
    await init_db()
    # start background scheduler for CauHinhThongBao
    app.state._cauhinh_task = asyncio.create_task(_cauhinh_scheduler())

async def _cauhinh_scheduler():
    """Chạy lúc 8h sáng mỗi ngày"""
    log.info("CauHinhThongBao scheduler started; run every day at 08:00")
    while True:
        try:
            now = datetime.now()
            # thời điểm 8h sáng hôm nay
            next_run = now.replace(hour=8, minute=0, second=0, microsecond=0)

            if now >= next_run:
                # nếu đã qua 8h hôm nay thì đặt sang 8h ngày mai
                next_run += timedelta(days=1)

            # thời gian còn lại để chờ
            wait_seconds = (next_run - now).total_seconds()
            log.info("Next run scheduled at %s (in %.2f seconds)", next_run, wait_seconds)

            await asyncio.sleep(wait_seconds)

            # tạo session và chạy
            async with AsyncSessionLocal() as session:
                svc = CauHinhThongBaoService(session)
                try:
                    sent = await svc.run_check_and_send()
                    if sent:
                        log.info("CauHinhThongBao: sent %d notifications", sent)
                    else:
                        log.info("CauHinhThongBao: no notifications to send")
                except Exception:
                    log.exception("Error while running CauHinhThongBao.run_check_and_send")

        except asyncio.CancelledError:
            log.info("CauHinhThongBao scheduler cancelled")
            break
        except Exception:
            log.exception("Unexpected error in CauHinhThongBao scheduler loop")
            await asyncio.sleep(60)  # nếu lỗi thì chờ 1 phút rồi thử lại
# async def _cauhinh_scheduler(interval_seconds: int = 60):
#     """Background loop that runs RunCheckAndSend periodically using a fresh AsyncSession."""
#     log.info("CauHinhThongBao scheduler started; interval=%s seconds", interval_seconds)
#     while True:
#         try:
#             async with AsyncSessionLocal() as session:
#                 svc = CauHinhThongBaoService(session)
#                 try:
#                     sent = await svc.run_check_and_send()
#                     if sent:
#                         log.info("CauHinhThongBao: sent %d notifications", sent)
#                     else:
#                         log.info("CauHinhThongBao: no notifications to send")
#                 except Exception:
#                     log.exception("Error while running CauHinhThongBao.run_check_and_send")
#             await asyncio.sleep(interval_seconds)
#         except asyncio.CancelledError:
#             log.info("CauHinhThongBao scheduler cancelled")
#             break
#         except Exception:
#             log.exception("Unexpected error in CauHinhThongBao scheduler loop")
#             await asyncio.sleep(interval_seconds)


@app.on_event("shutdown")
async def shutdown_event():
    # cancel background task
    task = getattr(app.state, '_cauhinh_task', None)
    if task:
        task.cancel()
        try:
            await task
        except Exception:
            pass


# Routers
app.include_router(auth.router, prefix="/api/Auth", tags=["auth"])
app.include_router(
    users.router,
    prefix="/api/User",
    tags=["users"],
    dependencies=[Depends(get_current_user)]  # ✅ tất cả endpoint users cần login
)

app.include_router(
    email_thong_bao.router,
    prefix="/api/EmailThongBao",
    tags=["email-thong-bao"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    nhan_vien.router,
    prefix="/api/NhanVien",
    tags=["nhan-vien"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    ngay_le.router,
    prefix="/api/NgayLe",
    tags=["ngay-le"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    thong_bao.router,
    prefix="/api/ThongBao",
    tags=["thong-bao"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    cau_hinh_thong_bao.router,
    prefix="/api/CauHinhThongBao",
    tags=["cau-hinh-thong-bao"],
    dependencies=[Depends(get_current_user)]
)
# Test root có yêu cầu auth
@app.get("/", dependencies=[Depends(get_current_user)])
async def root():
    return {"message": "qlnv-fastapi running"}


# 🔧 Custom OpenAPI để hiển thị Bearer Auth mặc định
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes
    )

    # Định nghĩa Bearer Auth
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Áp dụng BearerAuth cho toàn bộ API
    for path in openapi_schema.get("paths", {}).values():
        for op in path.values():
            op.setdefault("security", [{"HTTPBearer": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Gán custom openapi cho app
app.openapi = custom_openapi
