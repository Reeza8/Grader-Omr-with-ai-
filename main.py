from db import engine, Base
from Exam.Api.ExamApi import router as ExamRouter
from User.Api.UserAdminApi import router as UserAdminRouter
from fastapi import FastAPI, Request
from User.models import *
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc: RequestValidationError):
    # استخراج فیلدهای ارسال نشده
    missing_fields = [error["loc"][-1] for error in exc.errors() if error["type"] == "missing"]

    # استخراج خطاهای مربوط به طول کوتاه رشته
    short_fields = [
        error["loc"][-1] for error in exc.errors() if error["type"] == "string_too_short"
    ]

    # ساخت پیام "فیلدهای ارسال نشده" و "فیلدهایی که طول کوتاه دارند"
    if missing_fields:
        detail_message = f"فیلد های {', '.join(missing_fields)} ارسال نشدند"
    elif short_fields:
        detail_message = f"{', '.join(short_fields)} باید حداقل 8 کاراکتر باشد"
    else:
        detail_message = "خطا در اعتبارسنجی ورودی‌ها"

    return JSONResponse(
        status_code=400,
        content={
            "detail": detail_message,
            "message": exc.errors(),
        }
    )


app.include_router(UserAdminRouter, prefix="/user")
app.include_router(ExamRouter, prefix="/exam")

@app.get("/")
async def root():
    return {"message": f"Holllaaaaaaaaaa World "}

