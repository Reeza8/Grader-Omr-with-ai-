from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi import UploadFile, Form, File

class addUser(BaseModel):
    username: str

class ExamCreate(BaseModel):
    teacher_id: int
    name: str
    hasKey: Optional[bool] = False

class ExamUpdate(BaseModel):
    id : int
    name: Optional[str]
    haskey: Optional[bool] = False

class ExamOut(BaseModel):
    id: int
    teacher_id: int
    name: str
    createdAt: datetime
    modifiedAt: Optional[datetime]
    hasKey: bool

    class Config:
        orm_mode = True

class StudentExamCreate(BaseModel):
    exam_id: int
    student_id: int
    score: int
    correct: int
    incorrect: int
    empty: int

class StudentExamOut(BaseModel):
    id: int
    exam_id: int
    student_id: int
    score: int
    correct: int
    incorrect: int
    empty: int

    class Config:
        orm_mode = True

class CorrectSchema(BaseModel):
    img: UploadFile
    exam_id : int
    teacher_id: int

class UploadKey(BaseModel):
    exam_id: int
    teacher_id: int
    img: UploadFile
