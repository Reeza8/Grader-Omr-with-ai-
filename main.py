from db import engine, Base
from Exam.Api.ExamApi import router as ExamRouter
from User.Api.UserAdminApi import router as UserAdminRouter
from fastapi import FastAPI, Request
from User.models import *
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)





@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request, exc: ValidationError):
    fields_with_errors = []
    for error in exc.errors():
        field_name = error.get("loc")
        field_msg = error.get("msg")
        fields_with_errors.append({"field_name": field_name, "field_msg": field_msg})
    return JSONResponse(fields_with_errors,status_code=400)


app.include_router(UserAdminRouter, prefix="/user")
app.include_router(ExamRouter, prefix="/exam")

@app.get("/")
async def root():

    return {"message": f"Helllaaaaaaaaaao World "}

