from db import engine, Base
from Exam.Api.ExamApi import router as ExamRouter
from User.Api.UserApi import router as UserAdminRouter
from fastapi import FastAPI, Request
from User.models import *
from middleware.responseMiddleware import *
from middleware.authMiddleware import AuthMiddleware
from utils.utils import http_exception_handler, validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



# @app.exception_handler(ValueError)
# async def value_error_exception_handler(request: Request, exc: ValueError):
#     print("aggggggggggggggggggggggggggggggg")
#     return JSONResponse(
#         status_code=400,
#         content={"detail": str(exc)}
#     )


# @app.exception_handler(RequestValidationError)
# async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
#     errors = []
#     print("ddddddddddddd")
#     for error in exc.errors():
#         msg = error.get("msg")
#         if not isinstance(msg, str):
#             msg = str(msg)
#         error["msg"] = msg
#         errors.append(error)
#
#     detail_message = "خطا در اعتبارسنجی ورودی‌ها"
#
#     return JSONResponse(
#         status_code=400,
#         content={
#             "detail": detail_message,
#             "errors": errors
#         }
#     )


app.add_middleware(AuthMiddleware)
app.add_middleware(ResponseWrapperMiddleware)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(UserAdminRouter, prefix="/user")
app.include_router(ExamRouter, prefix="/exam")

@app.get("/")
async def root():
    return {"message": f"Holllaaaaaaaaaa World "}

