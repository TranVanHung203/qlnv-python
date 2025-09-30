from typing import Iterable, Optional, Tuple
import logging
from app.config import settings
import aiosmtplib
from email.message import EmailMessage

log = logging.getLogger(__name__)


class EmailSenderService:
    def __init__(self):
        # read SMTP settings from app.config
        self.host = settings.smtp_host
        self.port = settings.smtp_port or 25
        self.user = settings.smtp_user
        self.password = settings.smtp_pass
        self.from_addr = settings.smtp_from
        self.use_ssl = bool(settings.smtp_enable_ssl)

    async def send_email_async(self, to: str, subject: str, body: str, attachments: Optional[Iterable[Tuple[str, bytes]]] = None) -> bool:
        """Send an email asynchronously. Returns True on success, False on failure."""
        if not self.host or not self.from_addr:
            # If SMTP isn't configured, allow a simulated send in debug mode so scheduled runs still record ThongBao during development.
            if getattr(settings, 'debug', False):
                log.warning("SMTP settings not configured; DEBUG mode -> simulating send to %s", to)
                return True
            log.warning("SMTP settings not configured; skipping send to %s", to)
            return False

        msg = EmailMessage()
        msg["From"] = self.from_addr
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body, subtype="html")

        if attachments:
            for name, content in attachments:
                msg.add_attachment(content, maintype="application", subtype="octet-stream", filename=name)

        try:
            if self.use_ssl:
                # aiosmtplib supports start_tls separately; for true SSL use SMTP_SSL which aiosmtplib does not directly expose.
                # We'll use STARTTLS when use_ssl is True.
                await aiosmtplib.send(msg, hostname=self.host, port=self.port, username=self.user, password=self.password, start_tls=True)
            else:
                await aiosmtplib.send(msg, hostname=self.host, port=self.port, username=self.user, password=self.password)
            log.info("Email sent to %s subject=%s", to, subject)
            return True
        except Exception as ex:
            log.exception("Failed to send email to %s: %s", to, ex)
            return False
