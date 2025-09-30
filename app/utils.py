import smtplib
from email.message import EmailMessage
from app.config import settings
import asyncio
from typing import Optional


def _send_email_sync(to: str, subject: str, body: str, smtp_from: Optional[str] = None):
    if not settings.smtp_host or not settings.smtp_user:
        print("SMTP not configured, skipping send")
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = smtp_from or settings.smtp_from or settings.smtp_user
    msg['To'] = to
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port or 587) as s:
        s.starttls()
        s.login(settings.smtp_user, settings.smtp_pass)
        s.send_message(msg)


async def send_email(to: str, subject: str, body: str, smtp_from: Optional[str] = None):
    loop = asyncio.get_running_loop()
    # Offload blocking SMTP I/O to thread pool
    await loop.run_in_executor(None, _send_email_sync, to, subject, body, smtp_from)
