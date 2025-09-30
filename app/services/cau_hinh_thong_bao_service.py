from app.repositories.cau_hinh_thong_bao_repository import CauHinhThongBaoRepository
from app.schemas.cau_hinh_thong_bao import CauHinhThongBaoDto, CreateCauHinhThongBaoDto, UpdateCauHinhThongBaoDto
from app.models.cau_hinh_thong_bao import CauHinhThongBao
from app.repositories.nhan_vien_repository import NhanVienRepository
from app.repositories.ngay_le_repository import NgayLeRepository
from app.repositories.email_thong_bao_repository import EmailThongBaoRepository
from app.repositories.thong_bao_repository import ThongBaoRepository
from app.models.thong_bao import ThongBao
from datetime import datetime, timedelta
import itertools
from typing import Set, Tuple
from sqlalchemy import select
import logging
from app.services.email_sender import EmailSenderService
import openpyxl
from io import BytesIO
from html import escape

log = logging.getLogger(__name__)

class CauHinhThongBaoService:
    def __init__(self, session):
        self.repo = CauHinhThongBaoRepository(session)

    async def get_all_configs_async(self):
        configs = await self.repo.get_all_async()
        return [CauHinhThongBaoDto(
            id=c.id,
            so_ngay_thong_bao=c.so_ngay_thong_bao,
            danh_sach_nam_thong_bao=c.danh_sach_nam_thong_bao,
            is_active=c.is_active,
            exclude_saturday=c.exclude_saturday,
            exclude_sunday=c.exclude_sunday
        ) for c in configs]

    async def get_config_by_id_async(self, id: int):
        c = await self.repo.get_by_id_async(id)
        if c is None:
            return None
        return CauHinhThongBaoDto(
            id=c.id,
            so_ngay_thong_bao=c.so_ngay_thong_bao,
            danh_sach_nam_thong_bao=c.danh_sach_nam_thong_bao,
            is_active=c.is_active,
            exclude_saturday=c.exclude_saturday,
            exclude_sunday=c.exclude_sunday
        )

    async def get_active_only_async(self):
        c = await self.repo.get_async()
        if c is None:
            return None
        return CauHinhThongBaoDto(
            id=c.id,
            so_ngay_thong_bao=c.so_ngay_thong_bao,
            danh_sach_nam_thong_bao=c.danh_sach_nam_thong_bao,
            is_active=c.is_active,
            exclude_saturday=c.exclude_saturday,
            exclude_sunday=c.exclude_sunday
        )

    async def create_config_async(self, dto: CreateCauHinhThongBaoDto):
        cfg = CauHinhThongBao(
            so_ngay_thong_bao=dto.so_ngay_thong_bao,
            danh_sach_nam_thong_bao=dto.danh_sach_nam_thong_bao,
            is_active=dto.is_active,
            exclude_saturday=dto.exclude_saturday,
            exclude_sunday=dto.exclude_sunday
        )
        created = await self.repo.create_async(cfg)
        return CauHinhThongBaoDto(
            id=created.id,
            so_ngay_thong_bao=created.so_ngay_thong_bao,
            danh_sach_nam_thong_bao=created.danh_sach_nam_thong_bao,
            is_active=created.is_active,
            exclude_saturday=created.exclude_saturday,
            exclude_sunday=created.exclude_sunday
        )

    async def update_config_async(self, dto: UpdateCauHinhThongBaoDto):
        cfg = await self.repo.get_async()
        if cfg is None:
            cfg = CauHinhThongBao(
                so_ngay_thong_bao=dto.so_ngay_thong_bao,
                danh_sach_nam_thong_bao=dto.danh_sach_nam_thong_bao,
                is_active=dto.is_active,
                exclude_saturday=dto.exclude_saturday,
                exclude_sunday=dto.exclude_sunday
            )
            created = await self.repo.create_async(cfg)
            return CauHinhThongBaoDto(
                id=created.id,
                so_ngay_thong_bao=created.so_ngay_thong_bao,
                danh_sach_nam_thong_bao=created.danh_sach_nam_thong_bao,
                is_active=created.is_active,
                exclude_saturday=created.exclude_saturday,
                exclude_sunday=created.exclude_sunday
            )

        cfg.so_ngay_thong_bao = dto.so_ngay_thong_bao
        cfg.danh_sach_nam_thong_bao = dto.danh_sach_nam_thong_bao
        cfg.is_active = dto.is_active
        cfg.exclude_saturday = dto.exclude_saturday
        cfg.exclude_sunday = dto.exclude_sunday

        updated = await self.repo.update_async(cfg)
        return CauHinhThongBaoDto(
            id=updated.id,
            so_ngay_thong_bao=updated.so_ngay_thong_bao,
            danh_sach_nam_thong_bao=updated.danh_sach_nam_thong_bao,
            is_active=updated.is_active,
            exclude_saturday=updated.exclude_saturday,
            exclude_sunday=updated.exclude_sunday
        )

    async def delete_config_async(self, id: int):
        cfg = await self.repo.get_by_id_async(id)
        if cfg is None:
            raise KeyError("Not found")
        await self.repo.delete_async(cfg)

    def _count_working_days(self, start_date: datetime.date, end_date: datetime.date, holidays: Set[datetime.date], exclude_saturday: bool, exclude_sunday: bool) -> int:
        if end_date <= start_date:
            return 0
        count = 0
        d = start_date + timedelta(days=1)
        while d <= end_date:
            if d.weekday() == 5 and exclude_saturday:
                d += timedelta(days=1)
                continue
            if d.weekday() == 6 and exclude_sunday:
                d += timedelta(days=1)
                continue
            if d in holidays:
                d += timedelta(days=1)
                continue
            count += 1
            d += timedelta(days=1)
        return count

    async def run_check_and_send(self) -> int:
        """Implements the scheduled run: load config, employees, holidays, determine recipients, send emails with Excel attachment, and record ThongBao entries.

        Returns number of notifications sent (inserted).
        """
        # Load config
        cfg = await self.repo.get_async()
        so_ngay = cfg.so_ngay_thong_bao if cfg else 60

        # Repositories for other data
        nv_repo = NhanVienRepository(self.repo.session)
        ngay_le_repo = NgayLeRepository(self.repo.session)
        email_repo = EmailThongBaoRepository(self.repo.session)
        thongbao_repo = ThongBaoRepository(self.repo.session)

        # Load employees
        nv_res = await nv_repo.get_paged(1, 2147483647)
        employees = nv_res['items']

        # Load holidays
        holidays_paged = await ngay_le_repo.get_paged(1, 2147483647)
        holidays = set(itertools.chain.from_iterable(
            [
                [(n.ngay_bat_dau.date() + timedelta(days=i)) for i in range((n.ngay_ket_thuc.date() - n.ngay_bat_dau.date()).days + 1)]
                for n in holidays_paged['items']
            ]
        ))

        to_notify = []
        utc_now = datetime.utcnow().date()

        for nv in employees:
            try:
                if not getattr(nv, 'email', None) or not nv.email.strip():
                    continue

                join = nv.ngay_vao_lam.date()

                # Anniversary years from config
                years = []
                if cfg and cfg.danh_sach_nam_thong_bao:
                    parts = [p.strip() for p in cfg.danh_sach_nam_thong_bao.split(',') if p.strip()]
                    for p in parts:
                        try:
                            v = int(p)
                            if v > 0:
                                years.append(v)
                        except ValueError:
                            continue

                # Check anniversary years
                anniversary_handled = False
                reasons = []
                for y in years:
                    anniversary_date = join.replace(year=join.year + y)
                    if utc_now >= anniversary_date:
                        reasons.append(f"Kỷ niệm {y} năm làm việc")

                for reason in reasons:
                    to_notify.append((nv.id, nv.email, reason))
                    anniversary_handled = True

                if anniversary_handled:
                    continue

                # Probation logic: measure working days
                working_days = self._count_working_days(
                    join, utc_now, holidays,
                    exclude_saturday=getattr(cfg, 'exclude_saturday', True),
                    exclude_sunday=getattr(cfg, 'exclude_sunday', True)
                )
                if working_days >= so_ngay:
                    reason = f"Đã đủ {so_ngay} ngày làm việc (thử việc)"
                    to_notify.append((nv.id, nv.email, reason))

            except Exception:
                continue

        if not to_notify:
            return 0

        # HTML email template
        template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo thông báo nhân sự</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, Helvetica, sans-serif;">
    <table role="presentation" style="width: 100%; max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <tr>
            <td style="padding: 20px; text-align: center; background-color: #1e3a8a; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                <img src="https://atpro.com.vn/wp-content/uploads/2020/10/logo-cong-ty-1024x342-1024x342.png" alt="Company Logo" style="max-width: 150px; height: auto; margin-bottom: 10px; display: block; margin-left: auto; margin-right: auto;">
                <h1 style="color: #ffffff; font-size: 24px; margin: 0;">Báo cáo thông báo nhân sự</h1>
                <p style="color: #e5e7eb; font-size: 14px; margin: 5px 0;">Ngày gửi: {0}</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px;">
                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #3b82f6; color: #ffffff;">
                            <th style="padding: 12px; text-align: left; font-size: 14px; border: 1px solid #d1d5db;">Id</th>
                            <th style="padding: 12px; text-align: left; font-size: 14px; border: 1px solid #d1d5db;">Họ tên</th>
                            <th style="padding: 12px; text-align: left; font-size: 14px; border: 1px solid #d1d5db;">Email NV</th>
                            <th style="padding: 12px; text-align: left; font-size: 14px; border: 1px solid #d1d5db;">Lý do</th>
                        </tr>
                    </thead>
                    <tbody>
                        {1}
                    </tbody>
                </table>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px; text-align: center; background-color: #f9fafb; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
                <p style="color: #4b5563; font-size: 12px; margin: 0;">Đây là email tự động từ hệ thống nhân sự. Vui lòng không trả lời trực tiếp email này.</p>
            </td>
        </tr>
    </table>
</body>
</html>
"""

        # Generate table rows
        rows = []
        nv_map = {e.id: e for e in employees}
        row_index = 0
        notified_employees = set()
        cfg_emails = await email_repo.get_paged(1, 2147483647)
        recipients = [e.email for e in cfg_emails['items'] if getattr(e, 'email', None) and e.email.strip()]

        for recipient in recipients:
            for item in to_notify:
                key = (item[0], item[2].strip())
                if key in notified_employees:
                    continue
                already_sent = await thongbao_repo.exists_for_nhan_vien_with_reason(item[0], item[2], recipient)
                if not already_sent:
                    emp = nv_map.get(item[0])
                    name = getattr(emp, 'ten', '-') or '-'
                    email_nv = item[1] or '-'
                    row_style = "background-color: #f9fafb;" if row_index % 2 == 0 else ""
                    rows.append(
                        f'<tr style="{row_style}">'
                        f'<td style="padding: 12px; border: 1px solid #d1d5db;">{item[0]}</td>'
                        f'<td style="padding: 12px; border: 1px solid #d1d5db;">{escape(name)}</td>'
                        f'<td style="padding: 12px; border: 1px solid #d1d5db;">{escape(email_nv)}</td>'
                        f'<td style="padding: 12px; border: 1px solid #d1d5db;">{escape(item[2])}</td>'
                        f'</tr>'
                    )
                    row_index += 1
                    notified_employees.add(key)

        # Format HTML body
        html_body = template.format(datetime.utcnow().strftime('%d/%m/%Y'), ''.join(rows))

        # Generate Excel file
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "ThongBao"
        ws.append(["Id", "Ten", "EmailNV", "LyDo"])
        added_employees = set()

        r = 2
        for recipient in recipients:
            for item in to_notify:
                key = (item[0], item[2].strip())
                if key in added_employees:
                    continue
                already_sent = await thongbao_repo.exists_for_nhan_vien_with_reason(item[0], item[2], recipient)
                if not already_sent:
                    emp = nv_map.get(item[0])
                    ws.append([
                        item[0],
                        getattr(emp, 'ten', '-') or '-',
                        item[1] or '-',
                        item[2]
                    ])
                    r += 1
                    added_employees.add(key)

        # Adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = max_length + 2
            ws.column_dimensions[column].width = adjusted_width

        # Save Excel to bytes
        excel_io = BytesIO()
        wb.save(excel_io)
        excel_bytes = excel_io.getvalue()

        if not recipients:
            return 0

        sent = 0
        emailer = EmailSenderService()
        subject = "Báo cáo thông báo nhân sự"
        attachments = [("ThongBao.xlsx", excel_bytes)]

        for recipient in recipients:
            try:
                items_for_recipient = []
                for item in to_notify:
                    already_sent = await thongbao_repo.exists_for_nhan_vien_with_reason(item[0], item[2], recipient)
                    if not already_sent:
                        items_for_recipient.append(item)

                if not items_for_recipient:
                    continue

                # Send email
                await emailer.send_email_async(recipient, subject, html_body, attachments=attachments)

                # Log notifications
                for item in items_for_recipient:
                    await thongbao_repo.create(
                        ThongBao(
                            nhan_vien_id=item[0],
                            email_nhan=recipient,
                            ngay_gui=datetime.utcnow(),
                            ly_do=item[2]
                        )
                    )
                    sent += 1

            except Exception as e:
                log.exception("Failed to send email to %s", recipient)
                continue

        return sent