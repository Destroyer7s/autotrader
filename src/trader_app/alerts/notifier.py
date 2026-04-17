from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

import requests

LOGGER = logging.getLogger(__name__)


class Notifier:
    def __init__(self, discord_webhook_url: str = "") -> None:
        self.discord_webhook_url = discord_webhook_url

    def notify_discord(self, message: str) -> bool:
        if not self.discord_webhook_url:
            return False
        try:
            response = requests.post(
                self.discord_webhook_url,
                json={"content": message},
                timeout=10,
            )
            response.raise_for_status()
            return True
        except Exception as exc:
            LOGGER.warning("Discord notification failed: %s", exc)
            return False

    def notify_email(
        self,
        message: str,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        to_email: str,
        from_email: str,
    ) -> bool:
        if not (smtp_host and smtp_user and smtp_password and to_email and from_email):
            return False

        msg = EmailMessage()
        msg["Subject"] = "AutoTrader Alert"
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(message)

        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            return True
        except Exception as exc:
            LOGGER.warning("Email notification failed: %s", exc)
            return False
