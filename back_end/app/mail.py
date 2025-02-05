from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiosmtplib import SMTP
from pydantic import BaseModel, Field

from .config import MAIL_FROM_ADDRESS, MAIL_SMTP_HOSTNAME, MAIL_SMTP_PASSWORD, MAIL_SMTP_PORT, MAIL_SMTP_USERNAME

if MAIL_SMTP_USERNAME is None or MAIL_SMTP_PASSWORD is None or MAIL_SMTP_PORT is None:
    raise Exception("Mail config missing, check .env")


class EmailDetails(BaseModel):
    sender: str = Field(description="Sender.", default=MAIL_FROM_ADDRESS)
    to: str = Field(description="Receiver.")
    subject: str = Field(description="Subject of the email.")
    content: str = Field(description="The HTML email content.")


async def get_smtp_client():
    client = SMTP(hostname=MAIL_SMTP_HOSTNAME, port=MAIL_SMTP_PORT, use_tls=True)
    await client.connect()

    await client.login(username=MAIL_SMTP_USERNAME, password=MAIL_SMTP_PASSWORD)
    try:
        yield client
    finally:
        await client.quit()


async def send_mail(mail_client: SMTP, email_details: EmailDetails):
    email_message = MIMEMultipart()
    email_message["From"] = email_details.sender
    email_message["To"] = email_details.to
    email_message["Subject"] = email_details.subject
    email_message.attach(MIMEText(email_details.content, "html"))

    # Attach header image
    with open("app/services/email_generator/images/email_header.png", "rb") as file:
        header_img = MIMEImage(file.read(), 'png')
        header_img.add_header('Content-ID', '001')
        header_img.add_header('Content-Disposition', 'inline', filename="header.png")
        email_message.attach(header_img)

    return await mail_client.send_message(email_message)
