from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from Exam.models import Exam, ExamKey
from Exam.Schema.ExamSchema import ExamCreate, ExamUpdate, ExamOut, CorrectSchema, UploadKey
from db import get_async_session
from fastapi.responses import JSONResponse
from starlette.datastructures import FormData
from utils import correction


router = APIRouter(prefix='/examApi')


@router.post("/addExam", response_model=ExamOut)
async def create_exam(exam: ExamCreate, session: AsyncSession = Depends(get_async_session)):
    # Query to check for duplicate exam
    exam_query = await session.execute(select(Exam).where(Exam.name == exam.name,Exam.teacher_id == exam.teacher_id))
    existing_exam = exam_query.scalars().first()

    if existing_exam:
        raise HTTPException(status_code=400, detail="نام آزمون تکراری است")

    # Create the new exam
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


@router.put("/editExam/", response_model=ExamOut)
async def update_exam(exam_update: ExamUpdate, session: AsyncSession = Depends(get_async_session)):
    # Query to check if the exam with the given ID exists
    exam_query = await session.execute(
        select(Exam)
        .where(Exam.id == exam_update.id)
    )
    exam = exam_query.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="ازمون یافت نشد")

    # Query to check if an exam with the same name and teacher_id exists, excluding the current exam ID
    duplicate_query = await session.execute(select(Exam)
        .where(Exam.name == exam_update.name, Exam.teacher_id == exam.teacher_id, Exam.id != exam_update.id))
    duplicate_exam = duplicate_query.scalars().first()
    if duplicate_exam:
        raise HTTPException(status_code=400, detail="نام آزمون تکراری است")

    # Update exam details
    for key, value in exam_update.dict(exclude_unset=True).items():
        setattr(exam, key, value)

    await session.commit()
    await session.refresh(exam)
    return exam


@router.delete("/deleteExam/{exam_id}")
async def delete_exam(exam_id: int, session: AsyncSession = Depends(get_async_session)):
    examQuery = await session.execute(select(Exam).where(Exam.id == exam_id))
    exam = examQuery.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="ازمون یافت نشد")

    await session.delete(exam)
    await session.commit()
    return {"detail": "ازمون با موفقیت حذف شد"}


@router.get('/correct/')
async def correct(request: Request, session: AsyncSession = Depends(get_async_session)):
    data = await request.form()
    if len(data) == 0:
        return JSONResponse("درخواست خالی میباشد")
    data = FormData(data)
    data = CorrectSchema(**data)
    examQuery = await session.execute(select(Exam).where(Exam.id == data.exam_id, Exam.teacher_id == data.teacher_id))
    exam = examQuery.scalar_one_or_none()
    if  not exam:
        raise HTTPException(status_code=404, detail="ازمون یافت نشد")
    if not exam.hasKey:
        raise HTTPException(status_code=400, detail="ازمون کلید ندارد")
    file_bytes = await data.img.read()

    score, codes=correction.scan(file_bytes, exam.key)

    return JSONResponse(f"{score} score  ,{codes} codes")

@router.post('/uploadKey/')
async def uploadKey(request: Request, session: AsyncSession = Depends(get_async_session)):
    data = await request.form()
    if len(data) == 0:
        return JSONResponse("درخواست خالی میباشد")
    data = UploadKey(**data)
    file_bytes = await data.img.read()
    key = correction.scanKey(file_bytes)
    examQuery = await session.execute(select(Exam).where(Exam.id == data.exam_id, Exam.teacher_id == data.teacher_id))
    exam = examQuery.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="ازمون یافت نشد")
    exam.key = key
    exam.hasKey = True
    await session.commit()
    await session.refresh(exam)

    for question_number, right_choice in enumerate(key):
        new_exam_key = ExamKey(
            exam_id=data.exam_id,
            questionNumber=question_number,
            rightChoice=right_choice
        )
        session.add(new_exam_key)

    await session.commit()
    return JSONResponse(key)

