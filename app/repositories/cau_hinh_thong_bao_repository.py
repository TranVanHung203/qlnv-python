from app.models.cau_hinh_thong_bao import CauHinhThongBao

from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession


class CauHinhThongBaoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_async(self):
        q = select(CauHinhThongBao).where(CauHinhThongBao.is_active == True).order_by(CauHinhThongBao.id.desc()).limit(1)
        res = await self.session.execute(q)
        cfg = res.scalars().first()
        if cfg is not None:
            return cfg

        # fallback chỉ khi bảng rỗng
        count = await self.session.scalar(select(func.count()).select_from(CauHinhThongBao))
        if count == 0:
            return None

        return None  # không trả về config inactive


    async def get_all_async(self):
        q = select(CauHinhThongBao).order_by(CauHinhThongBao.id.desc())
        res = await self.session.execute(q)
        return res.scalars().all()

    async def get_by_id_async(self, id: int):
        q = select(CauHinhThongBao).where(CauHinhThongBao.id == id)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def create_async(self, cfg: CauHinhThongBao):
        # deactivate others
        others_q = select(CauHinhThongBao).where(CauHinhThongBao.is_active == True)
        others = (await self.session.execute(others_q)).scalars().all()
        for o in others:
            o.is_active = False

        cfg.is_active = True
        self.session.add(cfg)
        await self.session.commit()
        await self.session.refresh(cfg)
        return cfg

    async def update_async(self, cfg: CauHinhThongBao):
        if cfg.is_active:
            others_q = select(CauHinhThongBao).where(CauHinhThongBao.is_active == True, CauHinhThongBao.id != cfg.id)
            others = (await self.session.execute(others_q)).scalars().all()
            for o in others:
                o.is_active = False

        self.session.add(cfg)
        await self.session.commit()
        await self.session.refresh(cfg)
        return cfg

    async def delete_async(self, cfg: CauHinhThongBao):
        await self.session.delete(cfg)
        await self.session.commit()
