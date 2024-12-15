from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class AddTeacher(BaseModel):
    email: Optional[EmailStr] = None
    name: str
    username: str
    password: str = Field(..., min_length=8, description="رمز عبور باید حداقل 8 کاراکتر باشد")

class TeacherOperation(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    username: str
    password: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    id : int
    username: str
    # password: str
    class Config:
        from_attributes = True

class GetUser(BaseModel):
    id: int
    name : str
    studentCode : str
    teacher_id : int
    class Config:
        from_attributes = True

class EditStudent(BaseModel):
    id: int
    name : str


