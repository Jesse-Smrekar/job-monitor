from __future__ import annotations

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .config import AppConfig
from .scraper import JobPosting

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def notify(config: AppConfig, jobs: list[JobPosting]) -> None:
    if not jobs:
        return

    if config.smtp_user and config.notify_email:
        send_email(config, jobs)
    else:
        logger.warning("Email not configured — skipping email notification")

    if config.desktop_notify:
        send_desktop_notification(jobs, config.desktop_notify_url, config.desktop_notify_sound)


def send_email(config: AppConfig, jobs: list[JobPosting]) -> None:
    html = _render_email(jobs)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Job Monitor: {len(jobs)} new posting(s)"
    msg["From"] = config.smtp_from or config.smtp_user
    msg["To"] = config.notify_email
    msg.attach(MIMEText(html, "html"))

    try:
        if config.smtp_port == 465:
            with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as server:
                server.login(config.smtp_user, config.smtp_password)
                server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        else:
            with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.login(config.smtp_user, config.smtp_password)
                server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        logger.info("Email sent to %s (%d jobs)", config.notify_email, len(jobs))
    except Exception:
        logger.exception("Failed to send email")


def send_desktop_notification(
    jobs: list[JobPosting],
    notification_url: str = "",
    notification_sound: bool = True,
) -> None:
    try:
        from winotify import Notification, audio  # type: ignore

        titles = [j.title for j in jobs[:3]]
        body = ", ".join(titles)
        if len(jobs) > 3:
            body += f" ... and {len(jobs) - 3} more"

        kwargs = dict(
            app_id="Job Monitor",
            title=f"{len(jobs)} new job(s) found",
            msg=body,
            duration="short",
            launch=(notification_url if notification_url else ""),
        )
        # if notification_url:
        #     kwargs["launch"] = notification_url

        toast = Notification(**kwargs)

        if notification_sound:
            toast.set_audio(getattr(audio, "Default"), loop=False)

        toast.show()
    except Exception:
        logger.exception("Failed to send desktop notification")


def _render_email(jobs: list[JobPosting]) -> str:
    env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=True)
    template = env.get_template("email_digest.html")
    return template.render(
        jobs=jobs,
        count=len(jobs),
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
