import smtplib
from email.mime.text import MIMEText
from typing import List
from loguru import logger

from src.core.config import settings


class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.email = settings.SMTP_EMAIL
        self.password = settings.SMTP_PASSWORD

    def send_email(self, subject: str, body: str, recipients: List[str]) -> bool:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = ", ".join(recipients)
        logger.debug(f"Sending {subject} email to {', '.join(recipients)}")

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(self.email, self.password)
                smtp.sendmail(from_addr=self.email, to_addrs=recipients, msg=msg.as_string())
            logger.info("Email sent successfully.")
            return True
        except Exception as e:
            logger.exception(f"Failed to send email: {e}")
            return False

    async def reset_password(self, reset_token: str, email: str, host: str, reg: bool = False) -> bool:
        if reg:
            logger.info(f"Confirm reg email to {email}, {reset_token=}")
            subject = "Confirmation of Registration"
            url = f"{host}/confirmation_of_registration/{reset_token}"
            body = f"To confirm your registration, follow the link:\n{url}"
        else:
            logger.info(f"Send reset email to {email}, {reset_token=}")
            subject = "Password Reset"
            url = f"{host}/reset_password/{reset_token}"
            body = f"To reset your password, follow the link:\n{url}"

        recipients = [email]
        return self.send_email(subject, body, recipients)


email_service = EmailService()
