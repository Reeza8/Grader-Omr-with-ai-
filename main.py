from db import engine, Base
from Exam.Api.ExamApi import router
from fastapi import FastAPI
from Exam.models import *
from User.models import *
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)




app.include_router(router, prefix="/exam")

@app.get("/")
async def root():

    return {"message": f"Helllaaaaaaaaaao World "}

