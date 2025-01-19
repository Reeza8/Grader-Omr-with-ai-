from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from Exam.models import Exam, ExamKey, Student_Exam
from Exam.Schema.ExamSchema import GetExams, CorrectSchema, UploadKey, ExamCreate, ExamUpdate, GetExamKey, GetExamDetail, StudentDetail, GetExamDetail
from db import get_async_session
from fastapi.responses import JSONResponse, FileResponse
from starlette.datastructures import FormData
from utils import correction
from User.models import User, Student
import json
import os



router = APIRouter(prefix='/examApi')

ERROR_IMAGES_DIR = "error_images"
SUCCESS_IMAGES_DIR = "success_images"

os.makedirs(ERROR_IMAGES_DIR, exist_ok=True)
os.makedirs(SUCCESS_IMAGES_DIR, exist_ok=True)


@router.post("/addExam", response_model=GetExams)
async def addExam(exam: ExamCreate, session: AsyncSession = Depends(get_async_session)):
    # Check for duplicate exam
    exam_query = await session.execute(select(Exam).where(Exam.name == exam.name, Exam.teacher_id == exam.teacher_id))
    existing_exam = exam_query.scalars().first()

    if existing_exam:
        raise HTTPException(status_code=400, detail="نام آزمون تکراری است")

    new_exam = Exam(**exam.dict())
    session.add(new_exam)
    await session.commit()
    await session.refresh(new_exam)

    # Log output
    print("AddExam Response:", GetExams.from_orm(new_exam).dict())

    return new_exam

@router.get("/getExam/{exam_id}", response_model=GetExamDetail)
async def getExam(exam_id: int, session: AsyncSession = Depends(get_async_session)):
    # Get exam and student count
    exam_query = await session.execute(
        select(
            Exam,
            func.count(Student_Exam.id).label("student_count")
        )
        .join(Student_Exam, Student_Exam.exam_id == Exam.id, isouter=True)
        .where(Exam.id == exam_id)
        .group_by(Exam.id)
    )
    exam_result = exam_query.first()
    if not exam_result:
        raise HTTPException(status_code=404, detail="ازمون یافت نشد")

    exam, student_count = exam_result
    question_count = len(exam.key) if exam.hasKey else 0

    # Get student details
    student_details_query = await session.execute(
        select(
            Student_Exam.student_id,
            Student_Exam.score,
            Student_Exam.correct,
            Student_Exam.incorrect,
            Student_Exam.empty,
            User.name,
            Student.studentCode,
        )
        .join(Student, Student_Exam.student_id == Student.id)
        .join(User, Student.id == User.id)
        .where(Student_Exam.exam_id == exam.id)
    )
    student_details = [
        StudentDetail(
            student_id=detail.student_id,
            score=detail.score,
            correct=detail.correct,
            incorrect=detail.incorrect,
            empty=detail.empty,
            name=detail.name,
            studentCode=detail.studentCode,
        )
        for detail in student_details_query
    ]

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

    # Log output
    print("GetExam Response:", json.dumps(response.dict(), ensure_ascii=False, default=str))

    return response

@router.get("/getExams/{teacher_id}", response_model=List[GetExams])
async def getExams(teacher_id: int,queryString: Optional[str] = Query(None),session: AsyncSession = Depends(get_async_session)):
    exams_query = select(
        Exam,
        func.count(Student_Exam.id).label("student_count")
    ).join(Student_Exam, Student_Exam.exam_id == Exam.id, isouter=True)

    if queryString:
        exams_query = exams_query.where(Exam.name.ilike(f"%{queryString}%"))

    exams_query = exams_query.where(Exam.teacher_id == teacher_id).group_by(Exam.id)

    exams_with_counts = await session.execute(exams_query)
    exams_with_counts = exams_with_counts.all()

    exams = []
    for exam, student_count in exams_with_counts:
        exam.studentCount = student_count
        if exam.hasKey:
            exam.questionNumber = len(exam.key)
        exams.append(exam)

    # Log output
    print("GetExams Response:",
          json.dumps([GetExams.from_orm(exam).dict() for exam in exams], ensure_ascii=False, default=str))

    return exams

@router.put("/editExam/", response_model=GetExams)
async def editExam(exam_update: ExamUpdate, session: AsyncSession = Depends(get_async_session)):
    # Check if exam exists
    exam_query = await session.execute(
        select(Exam)
        .where(Exam.id == exam_update.id)
    )
    exam = exam_query.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="ازمون یافت نشد")

    # Check for duplicate name
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

    # Log output
    print("editExam Response:", GetExams.from_orm(exam).dict())

    return exam

@router.delete("/deleteExam/{exam_id}")
async def deleteExam(exam_id: int, session: AsyncSession = Depends(get_async_session)):
    examQuery = await session.execute(select(Exam).where(Exam.id == exam_id))
    exam = examQuery.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="ازمون یافت نشد")

    await session.delete(exam)
    await session.commit()

    # Log output
    print("DeleteExam Response:", {"exam_id": exam_id, "detail": "ازمون با موفقیت حذف شد"})

    return {"detail": "ازمون با موفقیت حذف شد"}

@router.get('/correctSheet/')
async def correct(request: Request, session: AsyncSession = Depends(get_async_session)):
    # Read input data
    data = await request.form()
    if not data:
        raise HTTPException(status_code=400, detail="درخواست خالی می‌باشد")

    data = FormData(data)
    data = CorrectSchema(**data)

    # Get exam
    exam_query = await session.execute(
        select(Exam).where(Exam.id == data.exam_id, Exam.teacher_id == data.teacher_id)
    )
    exam = exam_query.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="آزمون یافت نشد")
    if not exam.hasKey:
        raise HTTPException(status_code=400, detail="آزمون کلید ندارد")

    try:
        file_bytes = await data.img.read()
        score, correct, incorrect, codes = correction.scan(file_bytes, exam.key)
        success_image_path = os.path.join(SUCCESS_IMAGES_DIR, f"exam_{data.exam_id}.jpg")
        with open(success_image_path, "wb") as f:
            f.write(file_bytes)
        print(f"-----------Success image saved to {success_image_path}")
    except Exception as e:
        print(str(e))
        error_image_path = os.path.join(ERROR_IMAGES_DIR, f"exam_{data.exam_id}.jpg")
        with open(error_image_path, "wb") as f:
            f.write(file_bytes)
        print(f"-----------Error image saved to {error_image_path}")
        raise HTTPException(status_code=400, detail="خطا در پردازش پاسخ‌برگ" )

    empty = len(exam.key) - (correct + incorrect)

    # Get or create student
    student_query = await session.execute(
        select(Student).where(Student.studentCode == codes, Student.teacher_id == data.teacher_id)
    )
    student = student_query.scalar_one_or_none()

    if not student:
        student = Student(
            studentCode=codes,
            teacher_id=data.teacher_id,
            user=User(name="بدون نام")
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)

    student_exam_query = await session.execute(
        select(Student_Exam).where(Student_Exam.exam_id == data.exam_id, Student_Exam.student_id == student.id)
    )
    existing_student_exam = student_exam_query.scalar_one_or_none()

    if existing_student_exam:
        existing_student_exam.score = score
        existing_student_exam.correct = correct
        existing_student_exam.incorrect = incorrect
        existing_student_exam.empty = empty
        await session.commit()
        await session.refresh(existing_student_exam)
    else:
        new_student_exam = Student_Exam(
            exam_id=data.exam_id,
            student_id=student.id,
            score=score,
            correct=correct,
            incorrect=incorrect,
            empty=empty
        )
        session.add(new_student_exam)
        await session.commit()
        await session.refresh(new_student_exam)

    # Log output
    print("CorrectSheet Response:", {
        "exam_id": data.exam_id,
        "student_id":student.id,
        "code": codes,
        "score": score,
        "correct": correct,
        "incorrect": incorrect,
        "empty": empty
    })

    return JSONResponse(
        {
            "code": codes,
            "score": score,
            "correct": correct,
            "incorrect": incorrect,
            "empty": empty
        }
    )

@router.post('/uploadKey/')
async def uploadKey(request: Request, session: AsyncSession = Depends(get_async_session)):
    # خواندن داده‌های ورودی
    data = await request.form()
    if not data:
        raise HTTPException(status_code=400, detail="درخواست خالی می‌باشد")

    data = UploadKey(**data)

    try:
        file_bytes = await data.img.read()
        key = correction.scanKey(file_bytes)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail="خطا در پردازش پاسخ‌برگ")

    # جستجوی آزمون
    exam_query = await session.execute(
        select(Exam).where(Exam.id == data.exam_id, Exam.teacher_id == data.teacher_id)
    )

    exam = exam_query.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="آزمون یافت نشد")

    # به‌روزرسانی کلید آزمون
    exam.key = key
    exam.hasKey = True
    await session.commit()
    await session.refresh(exam)

    # به‌روزرسانی کلید سوالات
    for question_number, right_choice in enumerate(key):
        exam_key_query = await session.execute(
            select(ExamKey).where(
                ExamKey.exam_id == data.exam_id,
                ExamKey.questionNumber == question_number
            )
        )
        existing_exam_key = exam_key_query.scalar_one_or_none()
        if existing_exam_key:
            existing_exam_key.rightChoice = right_choice
        else:
            session.add(ExamKey(
                exam_id=data.exam_id,
                questionNumber=question_number,
                rightChoice=right_choice
            ))

    await session.commit()

    print("uploadKey Response:", GetExamKey.from_orm(exam).dict())
    return GetExamKey.from_orm(exam)

@router.get("/download")
async def download_exam():
    pdf_path = "exam sheet.pdf"
    try:
        return FileResponse(pdf_path, media_type='application/pdf', filename="برگه ازمون.pdf")
    except Exception as e:
        raise HTTPException(status_code=400, detail="امکان دانلود پاسخبرگ نیست", message=str(e))

@router.get('/downloadErrorImage/{image_name}')
async def download_error_image(image_name: str):
    file_path = os.path.join(ERROR_IMAGES_DIR, image_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="تصویر موردنظر یافت نشد")
    return FileResponse(file_path, media_type='image/jpeg', filename=image_name)