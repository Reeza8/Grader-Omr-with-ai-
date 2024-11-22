from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Teacher class with foreign key to User
class Teacher(Base):
    __tablename__ = 'teacher'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    teacher_code = Column(String, unique=True, nullable=False)

    # Define a one-way relationship to User
    user = relationship('User', foreign_keys=[id])

# Student class with foreign key to Useraaa
class Student(Base):
    __tablename__ = 'student'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    student_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Define a one-way relationship to User
    user = relationship('User', foreign_keys=[id])
