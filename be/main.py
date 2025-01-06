from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from . import init_db
from typing import Optional
from fastapi import Header, HTTPException
from fastapi.responses import StreamingResponse
import json
from .model import RequestBody
from .modules import (
    get_user_repos, 
    get_user_commits, 
    save_repo_and_commits, 
    check_repo_update_needed,
    validate_date_n_token,
    get_total_commit_num, 
    get_specific_repo_commit_num,
    get_active_days,
    get_longest_streak,
    get_longest_gap,
    get_total_days,
    get_each_day_commit_count,
    get_latest_commit_sha
)
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5173/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "working!"}


# @app.get("/save/{github_username}/all/{year}/{month}")
# async def get_repo_n_commits_then_save_to_db(
#     github_username: str,
#     year: int,
#     month: int,
#     github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
# ):
    
#     start_date, end_date = validate_date_n_token(github_username, year, month, github_token)

#     # 레포 정보 가져오기
#     repos = get_user_repos(github_token, start_date, end_date)
    
#     if isinstance(repos, list):
#         try:
#             for repo in repos:
#                 # 레포 업데이트 필요 여부 확인
#                 if check_repo_update_needed(github_username, repo['name'], repo['updated_at']):
#                     # 각 레포 커밋 정보 가져오기
#                     commits = get_user_commits(github_token, github_username, repo['name'], start_date, end_date)
                    
#                     if isinstance(commits, list):
#                         # 데이터베이스에 저장
#                         result = save_repo_and_commits(github_username, repo, commits)
#                         print(f"{result}\t| Repository {repo['name']} updated")
#                     else:
#                         print(f"err     | Error getting commits for {repo['name']}: {commits}")
#                 else:
#                     print(f"skip    | Repository {repo['name']} is up to date")
#         finally:
#             return {"success": True, "message": "done!"}
#     else:
#         return {"success": False, "message": "Error getting repositories"}


@app.get("/get/{github_username}/repo/{year}/{month}")
async def get_repository(
    github_username: str,
    year: int, 
    month: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    
    start_date, end_date = validate_date_n_token(github_username, year, month, github_token)

    # 해당 기간의 레포들 가져와서 바로 반환
    return get_user_repos(github_token, start_date, end_date)


@app.post("/save/{github_username}/specific/{year}/{month}")
async def save_specific_repo_n_commits_to_db(
    github_username: str,
    year: int,
    month: int,
    request_body: RequestBody,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    repository = request_body.repository.model_dump()
    start_date, end_date = validate_date_n_token(github_username, year, month, github_token)
    
    if check_repo_update_needed(github_username=github_username, repo_url=repository['html_url'], updated_at=repository['updated_at']):
        # DB에서 최신 커밋 SHA 가져오기
        latest_commit_sha = get_latest_commit_sha(github_username, repository['html_url']) 
        
        commits = get_user_commits(
            github_token, 
            github_username, 
            repository['name'], 
            start_date, 
            end_date,
            latest_commit_sha
        )
        
        if isinstance(commits, list):
            result = save_repo_and_commits(github_username, repository, commits)
            return {
                "success": True,
                "message": f"'{repository['name']}' is saved! {result}",
                "total_commits": len(commits)
            }
        else:
            return {
                "success": False,
                "message": f"Error getting commits for {repository['name']}: {commits}"
            }
    else:
        return {
            "success": True,
            "message": f"'{repository['name']}' is already up to date!"
        }


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

@app.get("/get/{user}/used_language")
async def get_used_language(
    user: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    start_date, end_date = validate_date_n_token(user, year, month, github_token)

    return get_used_language(user, start_date, end_date)

@app.get("/get/{user}/days/active/{year}/{month}")
async def get_active_days_endpoint(
    user: str,
    year: int,
    month: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    active_days = get_active_days(user, github_token, year, month)
    return {"active_days": active_days}

@app.get("/get/{user}/days/longest_streak/{year}/{month}")
async def get_longest_streak_endpoint(
    user: str,
    year: int,
    month: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    longest_streak = get_longest_streak(user, github_token, year, month)
    return {"longest_streak": longest_streak}

@app.get("/get/{user}/days/longest_gap/{year}/{month}/{day}")
async def get_longest_gap_endpoint(
    user: str,
    year: int,
    month: int,
    day: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    longest_gap = get_longest_gap(user, github_token, year, month, day)
    return {"longest_gap": longest_gap}

@app.get("/get/days/total/{year}/{month}")
async def get_total_days_endpoint(
    year: int,
    month: int,
):
    total_days = get_total_days(year, month)
    return {"total_days": total_days}

@app.get("/get/{user}/days/each/{year}/{month}")
async def get_each_day_commit_count_endpoint(
    user: str,
    year: int,
    month: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    each_day_commit_count = get_each_day_commit_count(user, github_token, year, month)
    return {"each_day_commit_count": each_day_commit_count}