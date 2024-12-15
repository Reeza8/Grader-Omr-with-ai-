from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from User.models import Teacher, User, Student
from passlib.context import CryptContext
from db import get_async_session
from User.Schema.UserAdminSchema import *

router = APIRouter(prefix='/userAdminApi')

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@router.post("/addTeacher", response_model=TeacherOperation)
async def addTeacher(teacher: AddTeacher, session: AsyncSession = Depends(get_async_session)):
    # چک ایمیل تکراری اضافه شد
    email_query = await session.execute(
        select(Teacher).where(Teacher.email == teacher.email)
    )
    existing_email = email_query.scalars().first()

    if existing_email:
        raise HTTPException(status_code=400, detail="ایمیل تکراری است")

    teacher_query = await session.execute(
        select(Teacher).where(Teacher.username == teacher.username)
    )
    existing_teacher = teacher_query.scalars().first()

    if existing_teacher:
        raise HTTPException(status_code=400, detail=" نام کاربری تکراری است")

    # Hash the password
    hashed_password = pwd_context.hash(teacher.password)

    # Create a new User and Teacher record
    new_user = User(name=teacher.name)
    session.add(new_user)
    await session.flush()  # Flush to get the new user ID

    new_teacher = Teacher(
        id=new_user.id,
        email=teacher.email,
        username=teacher.username,
        hashedPassword=hashed_password,
    )
    session.add(new_teacher)
    await session.commit()
    await session.refresh(new_teacher)
    new_teacher.password = teacher.password
    print("AddTeacher Response:", TeacherOperation.from_orm(new_teacher).dict())
    return new_teacher

@router.post("/login", response_model=LoginResponse)
async def login(loginData: LoginRequest, session: AsyncSession = Depends(get_async_session)):
    # Query the Teacher by username
    teacher_query = await session.execute(
        select(Teacher).where(Teacher.username == loginData.username)
    )
    teacher = teacher_query.scalar_one_or_none()

    if not teacher:
        raise HTTPException(status_code=404, detail="نام کاربری یافت نشد")

    # Verify the password
    if not pwd_context.verify(loginData.password, teacher.hashedPassword):
        raise HTTPException(status_code=401, detail="رمز عبور اشتباه است")

    # Create a mock token (replace with a real JWT implementation)
    response = LoginResponse.from_orm(teacher).dict()
    print("Login Response:", response)
    return teacher


@router.put("/editStudent/", response_model=GetUser)
async def editStudent(data: EditStudent, session: AsyncSession = Depends(get_async_session)):
    student_query = await session.execute(
        select(Student).where(Student.id == data.id)
    )
    student = student_query.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="دانش‌آموز پیدا نشد")
    user_query = await session.execute(
        select(User).where(User.id == data.id)
    )

    user = user_query.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="دانش‌آموز پیدا نشد")

    user.name = data.name
    await session.commit()
    await session.refresh(user)

    student.name = data.name

    response = GetUser.from_orm(student).dict()
    print("EditStudent Response:", response)

    return student
