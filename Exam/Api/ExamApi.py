from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from Exam.models import Exam, ExamKey, Student_Exam
from Exam.Schema.ExamSchema import GetExams, CorrectSchema, UploadKey, ExamCreate, ExamUpdate, GetExamKey, GetExamDetail, StudentDetail, GetExamDetail
from db import get_async_session
from fastapi.responses import JSONResponse
from starlette.datastructures import FormData
from utils import correction
from User.models import User, Student
from sqlalchemy.orm import joinedload


router = APIRouter(prefix='/examApi')


@router.post("/addExam", response_model=GetExams)
async def addExam(exam: ExamCreate, session: AsyncSession = Depends(get_async_session)):
    # Query to check for duplicate exam
    exam_query = await session.execute(select(Exam).where(Exam.name == exam.name, Exam.teacher_id == exam.teacher_id))
    existing_exam = exam_query.scalars().first()

    if existing_exam:
        raise HTTPException(status_code=400, detail="نام آزمون تکراری است")

    # Create the new exam
    new_exam = Exam(**exam.dict())
    session.add(new_exam)
    await session.commit()
    await session.refresh(new_exam)
    return new_exam




@router.get("/getExam/{exam_id}", response_model=GetExamDetail)
async def getExam(exam_id: int, session: AsyncSession = Depends(get_async_session)):
    # Get the exam details
    exam_query = await session.execute(select(Exam).where(Exam.id == exam_id))
    exam = exam_query.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # Get the number of questions if the exam has a key
    question_count = 0
    if exam.hasKey:
        question_count = len(exam.key)

    # Get the number of students
    student_count_query = await session.execute(
        select(func.count(Student_Exam.id)).where(Student_Exam.exam_id == exam.id)
    )
    student_count = student_count_query.scalar()

    # Get details for each student
    student_details_query = await session.execute(
        select(
            Student_Exam.student_id,
            Student_Exam.score,
            Student_Exam.correct,
            Student_Exam.incorrect,
            Student_Exam.empty,
            User.name,
            Student.studentCode,
        ).join(Student, Student_Exam.student_id == Student.id)
         .join(User, Student.id == User.id)
        .where(Student_Exam.exam_id == exam.id)
    )
    student_details = [
        StudentDetail(
            student_id=detail[0],
            score=detail[1],
            correct=detail[2],
            incorrect=detail[3],
            empty=detail[4],
            name=detail[5],
            studentCode=detail[6],
        )
        for detail in student_details_query.fetchall()
    ]

    # Build the response
    response = GetExamDetail(
        id=exam.id,
        name=exam.name,
        createdAt=exam.createdAt,
        modifiedAt=exam.modifiedAt,
        hasKey=exam.hasKey,
        studentCount=student_count,
        questionCount=question_count,
        students=student_details,
    )

    return response



@router.get("/getExams/{teacher_id}", response_model=List[GetExams])
async def getExams(teacher_id: int, session: AsyncSession = Depends(get_async_session)):
    examQuery = await session.execute(select(Exam).where(Exam.teacher_id == teacher_id))
    exams = examQuery.scalars().all()
    for exam in exams:
        student_count_query = await session.execute(
            select(func.count(Student_Exam.id)).where(Student_Exam.exam_id == exam.id)
        )
        studentCount = student_count_query.scalar()  # تعداد دانش‌آموزان
        exam.studentCount = studentCount  # مقداردهی تعداد دانش‌آموزان

        if exam.hasKey:
            questionNumber= len(exam.key)
            exam.questionNumber = questionNumber

    return exams

@router.put("/editExam/", response_model=GetExams)
async def editExam(exam_update: ExamUpdate, session: AsyncSession = Depends(get_async_session)):
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
                                            .where(Exam.name == exam_update.name, Exam.teacher_id == exam.teacher_id,
                                                   Exam.id != exam_update.id))
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
async def deleteExam(exam_id: int, session: AsyncSession = Depends(get_async_session)):
    examQuery = await session.execute(select(Exam).where(Exam.id == exam_id))
    exam = examQuery.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="ازمون یافت نشد")

    await session.delete(exam)
    await session.commit()
    return {"detail": "ازمون با موفقیت حذف شد"}


@router.get('/correctSheet/')
async def correct(request: Request, session: AsyncSession = Depends(get_async_session)):
    data = await request.form()
    if len(data) == 0:
        return JSONResponse("درخواست خالی میباشد")
    data = FormData(data)
    data = CorrectSchema(**data)
    examQuery = await session.execute(select(Exam).where(Exam.id == data.exam_id, Exam.teacher_id == data.teacher_id))
    exam = examQuery.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="ازمون یافت نشد")
    if not exam.hasKey:
        raise HTTPException(status_code=400, detail="ازمون کلید ندارد")
    file_bytes = await data.img.read()

    score, correct, incorrect, codes = correction.scan(file_bytes, exam.key)

    empty = len(exam.key) - (correct + incorrect)

    studentQuery = await session.execute(
        select(Student).where(Student.studentCode == codes, Student.teacher_id == data.teacher_id)
    )
    student = studentQuery.scalar_one_or_none()

    # ایجاد دانش‌آموز جدید در صورت عدم وجود
    if not student:
        student = Student(
            studentCode=codes,
            teacher_id=data.teacher_id,
            user=User(
                name="بدون نام",
            )
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)

    studentExamQuery = await session.execute(
        select(Student_Exam).where(Student_Exam.exam_id == data.exam_id, Student_Exam.student_id == student.id)
    )
    existingStudentExam = studentExamQuery.scalar_one_or_none()

    if existingStudentExam:
        # اگر رکورد وجود دارد، آن را به‌روزرسانی کن
        existingStudentExam.score = score
        existingStudentExam.correct = correct
        existingStudentExam.incorrect = incorrect
        existingStudentExam.empty = empty
        await session.commit()
        await session.refresh(existingStudentExam)
    else:
        newStudentExam = Student_Exam(
            exam_id=data.exam_id,  # مقدار exam_id
            student_id=student.id,  # مقدار student_id
            score=score,
            correct=correct,
            incorrect=incorrect,
            empty=empty
        )
        session.add(newStudentExam)
        await session.commit()
        await session.refresh(newStudentExam)

    return JSONResponse({"code" : codes,"score":score, "correct":correct, "incorrect":incorrect, "empty":empty })


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

    for questionNumber, rightChoice in enumerate(key):
        exam_key_query = await session.execute(
            select(ExamKey).where(
                ExamKey.exam_id == data.exam_id,
                ExamKey.questionNumber == questionNumber
            )
        )
        existing_exam_key = exam_key_query.scalar_one_or_none()

        if existing_exam_key:
            existing_exam_key.rightChoice = rightChoice
        else:
            # اگر وجود ندارد، رکورد جدید ایجاد کن
            new_exam_key = ExamKey(
                exam_id=data.exam_id,
                questionNumber=questionNumber,
                rightChoice=rightChoice
            )
            session.add(new_exam_key)

    await session.commit()

    await session.commit()

    return GetExamKey.from_orm(exam)

