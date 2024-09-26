from fastapi_users import schemas
from typing import Optional
from pydantic import BaseModel

# Extend Pydantic schemas for the user and user creation

class UserRead(schemas.BaseUser[int]):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    password: Optional[str]



class UserCreate(schemas.BaseUserCreate):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    password: Optional[str]


class User(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] =  None