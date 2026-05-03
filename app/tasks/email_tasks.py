from app.core.celery_app import celery_app
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText


@celery_app.task
def send_email_task(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL, to_email, msg.as_string())