import jwt
from datetime import datetime, timedelta
from utils.config import settings


def create_access_token(user_id: int, role: str, name:str) -> str:
    expire = datetime.utcnow() + timedelta(days=180)
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": expire,
        "name": name
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
