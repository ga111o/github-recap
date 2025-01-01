from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime
from .database import init_db
from typing import Optional
from fastapi import Header, HTTPException

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "working!"}


@app.get("/commits")
async def get_commits(
    year: int,
    month: int,
    user: str,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    if year is None or month is None or user is None:
        raise HTTPException(status_code=400, detail="Year, month and GitHub ID must be provided")
    
    current_year = datetime.now().year
    if year < 2005 or year > current_year or month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Invalid year or month")

    if github_token is not None:
        print("get token!")
        pass
  
    return {
        "code": 200,
        "message": "success",
        "year": year,
        "month": month,
        "user": user,
        "token_provided": github_token is not None
    }

