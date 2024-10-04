from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from Exam.models import Exam
from Exam.Schema.ExamSchema import ExamCreate, ExamUpdate, ExamOut
from db import get_async_session

router = APIRouter(prefix='/examApi')


@router.post("/addExam", response_model=ExamOut)
async def create_exam(exam: ExamCreate, session: AsyncSession = Depends(get_async_session)):
    new_exam = Exam(**exam.dict())
    session.add(new_exam)
    await session.commit()
    await session.refresh(new_exam)
    return new_exam


@router.get("/getExams/{teacher_id}", response_model=List[ExamOut])
async def get_user_exams(teacher_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Exam).where(Exam.teacher_id == teacher_id))
    exams = result.scalars().all()
    return exams


@router.put("/editExam/{exam_id}", response_model=ExamOut)
async def update_exam(exam_id: int, exam_data: ExamUpdate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    for key, value in exam_data.dict(exclude_unset=True).items():
        setattr(exam, key, value)

    await session.commit()
    await session.refresh(exam)
    return exam


@router.delete("/deleteExam/{exam_id}")
async def delete_exam(exam_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    await session.delete(exam)
    await session.commit()
    return {"detail": "Exam deleted successfully"}
