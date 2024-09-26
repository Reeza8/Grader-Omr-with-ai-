from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Column, String, Integer
from db import Base

class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = 'user'
    id= Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String)



