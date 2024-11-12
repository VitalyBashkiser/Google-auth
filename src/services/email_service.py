import smtplib
from email.mime.text import MIMEText
from typing import List
from loguru import logger

from src.core.config.email import smtp_settings
from src.enums.messages import Messages
from src.utils.template_renderer import render_message


class EmailService:
    def __init__(self):
        self.smtp_server = smtp_settings.SMTP_SERVER
        self.smtp_port = smtp_settings.SMTP_PORT
        self.email = smtp_settings.SMTP_EMAIL
        self.password = smtp_settings.SMTP_PASSWORD

    def send_email(self, subject: str, body: str, recipients: List[str]) -> bool:
        html_content = body.body.decode("utf-8")
        msg = MIMEText(html_content, "html")
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = ", ".join(recipients)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(self.email, self.password)
                smtp.sendmail(from_addr=self.email, to_addrs=recipients, msg=msg.as_string())
            return True
        except Exception as e:
            logger.exception(f"Failed to send templates: {e}")
            return False

    async def confirm_email(self, username: str, token: str, email: str, host: str, email_type: Messages) -> bool:
        """
        Send confirmation email for registration, password reset, or email change.

        Args:
            username (str): The user's name.
            token (str): The token for confirmation.
            email (str): The recipient's email.
            host (str): The host URL.
            email_type (Messages): The type of email to send (confirmation, password reset, or email change).
        """

        if email_type == Messages.EMAIL_CONFIRMATION:
            subject = "Confirm Your Registration"
            confirmation_url = f"{host}/auth/confirm-registration?token={token}"
            context = {"username": username, "confirmation_url": confirmation_url}

        elif email_type == Messages.PASSWORD_RESET:
            subject = "Password Reset"
            reset_url = f"{host}/auth/reset-password?token={token}"
            context = {"username": username, "reset_url": reset_url}

        elif email_type == Messages.CHANGE_EMAIL:
            subject = "Confirm Email Change"
            confirmation_url = f"{host}/auth/change-email?token={token}"
            context = {"username": username, "confirmation_url": confirmation_url}

        else:
            raise ValueError("Invalid email type")

        body = await render_message(email_type, context)
        recipients = [email]

        return self.send_email(subject, body, recipients)


email_service = EmailService()
