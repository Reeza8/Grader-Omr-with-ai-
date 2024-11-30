from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from datetime import datetime

class AddTeacher(BaseModel):
    email: Optional[EmailStr] = None
    name: str
    username: str
    password: str


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

class GetUser(BaseModel):
    id: int
    name : str
    studentCode : str
    teacher_id : int

class EditStudent(BaseModel):
    id: int
    name : str


