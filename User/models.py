from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())

# Teacher class with foreign key to User
class Teacher(Base):
    __tablename__ = 'teacher'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True, index=True)
    email =  Column(String, unique=True)
    username = Column(String, unique=True, nullable=False)
    hashedPassword = Column(String, nullable=False)

    # Define a one-way relationship to User
    user = relationship('User', foreign_keys=[id])

# Student class with foreign key to Useraaa
class Student(Base):
    __tablename__ = 'student'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    studentCode = Column(String, nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey('teacher.id'), nullable=False, index=True)
    # Define a one-way relationship to User
    user = relationship('User', foreign_keys=[id])
    teacher = relationship('Teacher', foreign_keys=[teacher_id])
