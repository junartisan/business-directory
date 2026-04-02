from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME = "no-reply@philippinescities.com",
    MAIL_PASSWORD = "XDV2mnx61_",
    MAIL_FROM = "admin@philippinescities.com",
    MAIL_PORT = 465,
    MAIL_SERVER = "mail.supremecluster.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_verification_email(email_to: EmailStr, token: str):
    # This is the link the user clicks
    verification_url = f"https://python.philippinescities.com/verify-email?token={token}"
    
    html = f"""
    <p>Thanks for registering with Philippines Cities Directory!</p>
    <p>Please click the link below to verify your account:</p>
    <a href="{verification_url}">Verify My Email</a>
    <p>This link will expire in 24 hours.</p>
    """

    message = MessageSchema(
        subject="Verify your Account",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)