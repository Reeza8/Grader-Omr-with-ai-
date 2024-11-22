from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from User.models import Teacher, User
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from db import get_async_session

router = APIRouter(prefix='/userAdminApi')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post('/addTeacher/')
async def add_teacher(username: str,email: str,password: str,teacher_code: str, session: AsyncSession = Depends(get_async_session),):
    """
    Service to add a new teacher and associate with a user.
    """
    hashed_password = pwd_context.hash(password)

    # Check if a user with the provided username or email already exists
    result = await session.execute(
        select(User).where((User.username == username) | (User.email == email))
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with the given username or email already exists.",
        )

    # Create User instance
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )
    session.add(new_user)
    await session.flush()  # Flush to generate user ID

    # Create Teacher instance
    try:
        new_teacher = Teacher(
            id=new_user.id,  # ForeignKey to User
            teacher_code=teacher_code,
        )
        session.add(new_teacher)
        await session.commit()
        await session.refresh(new_teacher)
        return {"message": "Teacher created successfully", "teacher_id": new_teacher.id}
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=400,
            detail="A teacher with the given teacher_code already exists.",
        )