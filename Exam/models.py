from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db import Base


class Exam(Base):
    __tablename__ = 'exam'

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey('teacher.id', ondelete='SET NULL'), nullable=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now())
    has_key = Column(Boolean, default=False)

    # Define a one-way relationship to Teacher
    teacher = relationship('Teacher', foreign_keys=[teacher_id])


class StudentExam(Base):
    __tablename__ = 'students_exam'

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey('exam.id', ondelete='SET NULL'), nullable=True)
    student_id = Column(Integer, ForeignKey('student.id', ondelete='SET NULL'), nullable=True)
    score = Column(Integer, nullable=False)
    correct = Column(Integer, nullable=False)
    incorrect = Column(Integer, nullable=False)
    empty = Column(Integer, nullable=False)

    # Define one-way relationships to Exam and Student
    exam = relationship('Exam', foreign_keys=[exam_id])
    student = relationship('Student', foreign_keys=[student_id])
