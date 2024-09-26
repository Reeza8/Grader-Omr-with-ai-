from typing import Optional
from urllib.request import Request
from fastapi_users.manager import BaseUserManager
from fastapi_users.db import SQLAlchemyUserDatabase
from models import User
from db import SessionLocal


class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = "SECRET_FOR_PASSWORD_RESET"
    verification_token_secret = "SECRET_FOR_EMAIL_VERIFICATION"
    def parse_id(self, id: str) -> int:
        try:
            return int(id)
        except ValueError:
            raise ValueError(f"Invalid user ID format: {id}")
    # Here you can override any necessary user manager methods
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    # You can also handle email verification logic here, if needed

async def get_user_db():
    async with SessionLocal() as session:
        yield SQLAlchemyUserDatabase(session, User)
