from src.services.email_service import email_service


async def notify_user(email: str, subject: str, message: str):
    await email_service.send_email(email, subject, message)
