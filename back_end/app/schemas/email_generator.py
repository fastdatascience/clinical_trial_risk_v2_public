from pydantic import BaseModel, Field


class EmailGeneratorBaseData(BaseModel):
    subject: str = Field(description="Subject of the email.")
    first_name: str = Field(description="The user's first name.")


class EmailGeneratorSignUpData(EmailGeneratorBaseData):
    otp: str = Field(description="The OTP code.")


class EmailGeneratorResetPasswordData(EmailGeneratorBaseData):
    reset_link: str = Field(description="The link to reset your password.")


class EmailGeneratorGeneralMessageData(EmailGeneratorBaseData):
    paragraphs: list[str] = Field(description="Paragraphs.")
