from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base
import enum


class UserRole(enum.Enum):
    teacher = "teacher"
    student = "student"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    phone_number = Column(String(13), unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    createdAt = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="user", uselist=False, foreign_keys="Student.user_id")
    students = relationship("Student", back_populates="teacher", foreign_keys="Student.teacher_id")


class Student(Base):
    __tablename__ = 'students'

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    student_code = Column(String(10), unique=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=False)

    user = relationship("User", back_populates="student", foreign_keys=[user_id])
    teacher = relationship("User", back_populates="students", foreign_keys=[teacher_id])


class VerifyCode(Base):
    __tablename__ = 'verify_code'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, nullable=False)
    isUsed = Column(Boolean, nullable=False, default=False)
    index = Column(String(256), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship('User', foreign_keys=[user_id])