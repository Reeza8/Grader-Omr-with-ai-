from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ExamCreate(BaseModel):
    teacher_id: int
    name: str
    has_key: Optional[bool] = False

class ExamUpdate(BaseModel):
    name: Optional[str]
    has_key: Optional[bool]

class ExamOut(BaseModel):
    id: int
    teacher_id: int
    name: str
    created_at: datetime
    modified_at: Optional[datetime]
    has_key: bool

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
