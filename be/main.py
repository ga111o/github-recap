from pathlib import Path
import sys

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from .database import init_db
from typing import Optional
from fastapi import Header, HTTPException

from be.modules import get_user_repos, get_user_commits, save_repo_and_commits, check_repo_update_needed
from be.modules import validate_date_n_token
from be.modules import get_total_commit_num, get_specific_repo_commit_num

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
@app.get("/get/{user}/commit_num/total")
async def get_commit_num(
    user: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    return get_total_commit_num(github_token, user, year, month)

@app.get("/get/{user}/commit_num/specific")
async def get_commit_num(
    user: str,
    repo_name: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    return get_specific_repo_commit_num(github_token, user, repo_name, year, month)