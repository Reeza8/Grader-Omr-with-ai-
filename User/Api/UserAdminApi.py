from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from User.models import Teacher, User
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from db import get_async_session
from User.Schema.UserAdminSchema import *

router = APIRouter(prefix='/userAdminApi')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/addTeacher", response_model=TeacherOperation)
async def addTeacher(teacher: AddTeacher, session: AsyncSession = Depends(get_async_session)):
    # Check for duplicate username or email

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

    return new_teacher

@router.post("/login", response_model=LoginResponse)
async def login(loginData: LoginRequest, session: AsyncSession = Depends(get_async_session)):
    # Query the Teacher by username
    teacher_query = await session.execute(
        select(Teacher).where(Teacher.username == loginData.username)
    )
    teacher = teacher_query.scalars_one_or_none(teacher_query)

    if not teacher:
        raise HTTPException(status_code=404, detail="نام کاربری یافت نشد")

    # Verify the password
    if not pwd_context.verify(loginData.password, teacher.hashedPassword):
        raise HTTPException(status_code=401, detail="رمز عبور اشتباه است")

    # Create a mock token (replace with a real JWT implementation)

    return teacher