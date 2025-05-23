from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db import Base


class Exam(Base):
    __tablename__ = 'exam'

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    name = Column(String, nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    modifiedAt = Column(DateTime(timezone=True), onupdate=func.now())
    hasKey = Column(Boolean, default=False)
    key = Column(JSON, nullable=True)

    # Define a one-way relationship to Teacher
    teacher = relationship('User', foreign_keys=[teacher_id])

class ExamKey(Base):
    __tablename__ = 'examKey'

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey('exam.id', ondelete='CASCADE'), nullable=True, index=True)
    questionNumber = Column(Integer)
    rightChoice = Column(Integer)
    exam = relationship('Exam', foreign_keys=[exam_id])


class Student_Exam(Base):
    __tablename__ = 'students_exam'

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey('exam.id', ondelete='SET NULL'), nullable=True, index=True)
    student_id = Column(Integer, ForeignKey('students.user_id', ondelete='SET NULL'), nullable=True, index=True)
    score = Column(Integer, nullable=False)
    correct = Column(Integer, nullable=False)
    incorrect = Column(Integer, nullable=False)
    empty = Column(Integer, nullable=False)

    # Define one-way relationships to Exam and Student
    exam = relationship('Exam', foreign_keys=[exam_id])
    student = relationship('Student', foreign_keys=[student_id])
