from pydantic import BaseModel


class addUser(BaseModel):
    username: str

class UserOperation(BaseModel):
    id: int
    username: str
