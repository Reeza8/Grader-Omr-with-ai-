from User.models import UserRole
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
import re



class LoginRequest(BaseModel):
    index: str = Field(..., alias="ایمیل یا شماره تلفن")

    class Config:
        populate_by_name = True

class EditStudent(BaseModel):
    id: int = Field(..., alias="شناسه دانش‌آموز")
    name: str = Field(..., alias="نام دانش‌آموز")

    class Config:
        populate_by_name = True

class VerifyCodeRequest(BaseModel):
    index: str = Field(..., alias="ایمیل یا شماره تلفن")
    code: str = Field(..., alias="کد تایید")

    class Config:
        populate_by_name = True

class EditPasswordRequest(BaseModel):
    password: str = Field(..., alias="رمز عبور جدید")
    repeatPassword: str = Field(..., alias="تکرار رمز عبور")
    previousPassword: Optional[str] = Field(None, alias="رمز عبور پیشین")

    class Config:
        populate_by_name = True

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        password_regex = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$')
        if not password_regex.match(v):
            raise ValueError("رمز عبور باید حداقل ۸ کاراکتر و شامل حروف و اعداد باشد.")
        return v

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.repeatPassword:
            raise ValueError("رمز عبور و تکرار آن یکسان نیستند.")
        return self

class EditNameRequest(BaseModel):
    name: str = Field(..., alias="نام")

    class Config:
        populate_by_name = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("نام نمی‌تواند خالی باشد.")
        if len(value) < 3:
            raise ValueError("نام باید حداقل 3 کاراکتر داشته باشد.")
        return value

class LoginPasswordRequest(BaseModel):
    index: str = Field(..., alias="ایمیل یا شماره تلفن")
    password: str = Field(..., alias="رمز عبور")

    class Config:
        populate_by_name = True

class ResetPasswordRequest(BaseModel):
    index: str = Field(..., alias="ایمیل یا شماره تلفن")

    class Config:
        populate_by_name = True



class LoginResponse(BaseModel):
    index: str
    role: UserRole

    class Config:
        from_attributes = True

class verifyCodeResponse(BaseModel):
    token: str
    index: str

class EditPasswordResponse(BaseModel):
    name: str | None
    user_id: int
    role: UserRole

class EditNameResponse(BaseModel):
    name: str
    user_id: int
    role: str

class LoginPasswordResponse(BaseModel):
    token: str
    index: str

class ResetPasswordResponse(BaseModel):
    user_id: int
    name: str
