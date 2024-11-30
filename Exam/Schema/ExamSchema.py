from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi import UploadFile

# class AddUser(BaseModel):
#     username: str


class ExamCreate(BaseModel):
    teacher_id: int
    name: str
    hasKey: Optional[bool] = False  # اختیاری


class ExamUpdate(BaseModel):
    id: int
    name: Optional[str] = None  # اختیاری
    hasKey: Optional[bool] = False  # اختیاری


class GetExams(BaseModel):
    id: int
    teacher_id: Optional[int] = 0  # اختیاری
    name: str
    createdAt: datetime
    modifiedAt: Optional[datetime] = None  # اختیاری
    hasKey: Optional[bool] = False  # اختیاری
    studentCount: Optional[int] = 0  # اختیاری
    questionNumber: Optional[int] = 0  # اختیاری

    class Config:
        from_attributes = True


class CorrectSchema(BaseModel):
    img: UploadFile
    exam_id: int
    teacher_id: int


class UploadKey(BaseModel):
    exam_id: int
    teacher_id: int
    img: UploadFile


class GetExamKey(BaseModel):
    id: int
    teacher_id: Optional[int] = 0  # اختیاری
    name: str
    createdAt: datetime
    modifiedAt: Optional[datetime] = None  # اختیاری
    hasKey: Optional[bool] = False  # اختیاری
    key: Optional[List] = []  # اختیاری

    class Config:
        from_attributes = True




class StudentDetail(BaseModel):
    student_id: int
    name: str
    studentCode: str
    score: float
    correct: int
    incorrect: int
    empty: int

class GetExamDetail(BaseModel):
    id: int
    name: str
    createdAt: datetime
    modifiedAt: Optional[datetime] = None
    hasKey: Optional[bool] = False
    studentCount: Optional[int] = 0
    questionCount: Optional[int] = 0
    students: List[StudentDetail] = []