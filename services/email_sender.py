"""Отправка email-уведомлений подписчикам и админу."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
logger = logging.getLogger(__name__)


class EmailSender:
    """Отправляет уведомления на email через SMTP."""

    def __init__(self, config: dict):
        """
        :param config: Секция email из sites.yaml:
            {
                "enabled": bool,
                "smtp_server": str,
                "smtp_port": int,
                "login": str,
                "password": str,
                "to_email": str,
            }
        """
        self.enabled: bool = bool(config.get("enabled", False))
        self.smtp_server: str = config.get("smtp_server", "")
        self.smtp_port: int = int(config.get("smtp_port", 587))
        self.login: str = config.get("login", "")
        self.password: str = config.get("password", "")
        self.to_email: str = config.get("to_email", "")

        if self.enabled and not all([self.smtp_server, self.login, self.password, self.to_email]):
            logger.warning("Email включён, но не все поля заполнены — отключаю")
            self.enabled = False

    async def send_notification(self, subject: str, html_body: str) -> bool:
        """Отправляет email админу."""
        if not self.enabled:
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.login
        msg["To"] = self.to_email

        text_part = MIMEText(self._strip_html(html_body), "plain", "utf-8")
        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(text_part)
        msg.attach(html_part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15) as server:
                server.starttls()
                server.login(self.login, self.password)
                server.sendmail(self.login, [self.to_email], msg.as_string())
            logger.info(f"✅ Email отправлен на {self.to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка отправки email: {e}")
            return False

    async def notify_admin_about_event(self, event: dict, teams_str: str, reason: str) -> bool:
        """Отправляет админу email о новом/изменившемся матче."""
        if not self.enabled:
            return False

        subject = self._make_subject(event, reason)
        body = self._make_html(event, teams_str, reason)
        return await self.send_notification(subject, body)

    async def notify_admin_about_error(self, site_name: str, error: str) -> bool:
        """Отправляет админу email об ошибке парсинга."""
        if not self.enabled:
            return False

        subject = f"⚠️ Ошибка парсера: {site_name}"
        body = f"<h3>Ошибка на сайте {site_name}</h3><pre>{error}</pre>"
        return await self.send_notification(subject, body)

    def _make_subject(self, event: dict, reason: str) -> str:
        prefix = {
            "new": "🏒 Новый матч",
            "available": "🎟 Билеты появились",
            "sold_out": "❌ Билеты закончились",
            "changed": "🔄 Изменение статуса",
        }.get(reason, "📢 Обновление")
        return f"{prefix}: {event.get('title', '')}"

    def _make_html(self, event: dict, teams_str: str, reason: str) -> str:
        price_min = event.get("price_min", "Не указана")
        price_max = event.get("price_max", "Не указана")
        if price_min == price_max:
            price = f"{price_min}"
        else:
            price = f"{price_min} – {price_max}"

        return f"""<html><body style="font-family:Arial,sans-serif;padding:20px;">
<h2 style="color:#0D398C;">{event.get('title', '')}</h2>
<table>
<tr><td><b>Команды:</b></td><td>{teams_str}</td></tr>
<tr><td><b>Дата:</b></td><td>{event.get('date', '')}</td></tr>
<tr><td><b>Место:</b></td><td>{event.get('place', '')}</td></tr>
<tr><td><b>Цена:</b></td><td>{price}</td></tr>
<tr><td><b>Статус:</b></td><td>{event.get('availability', '')}</td></tr>
</table>
<p><a href="{event.get('link', '')}" style="background:#0D398C;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Купить билет</a></p>
<hr><small>Вы получили это письмо как администратор системы мониторинга билетов.</small>
</body></html>"""

    @staticmethod
    def _strip_html(html: str) -> str:
        import re
        return re.sub(r"<[^>]+>", "", html).strip()
