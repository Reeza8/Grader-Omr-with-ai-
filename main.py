from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from user_manager import get_user_db, UserManager
from schema import UserRead,UserCreate
from db import SessionLocal, engine, Base
from models import User as User
import logging
from fastapi import FastAPI, Request
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

jwt_strategy = JWTStrategy(secret="YOUR_SECRET", lifetime_seconds=3600)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# Wrap JWTStrategy in AuthenticationBackend
auth_backend = AuthenticationBackend(
    name="jwt",  # The name for the authentication backend
    transport=bearer_transport,
    get_strategy=lambda: jwt_strategy  # Provide the get_strategy argument
)

# Basic logging setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("uvicorn.error")


# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     logger.info(f"Request: {request.method} {request.url}")
#
#     # Call the next middleware or endpoint
#     response = await call_next(request)
#
#     logger.info(f"Response status code: {response.status_code}")
#     return response



@app.get("/")
async def root():
    a = 5
    # Instead of print, consider using logging for async applications
    # If you need to perform any async operations, you can do it here
    print("awdadwdadwad")  # This will still block, consider using logging instead
    return {"message": f"Helllo Woraaaaaaaaaaaaaaaald {a}"}

def get_user_manager(user_db=Depends(get_user_db)):
    return UserManager(user_db)

# Initialize FastAPIUsers with user manager and JWT strategy
fastapi_users = FastAPIUsers(
    get_user_manager,
[auth_backend],  # Pass the auth backend, not a string
)


# Add registration and password reset endpoints
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
app.include_router(fastapi_users.get_auth_router(auth_backend))
app.include_router(fastapi_users.get_reset_password_router())

