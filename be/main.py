from pathlib import Path
import sys

root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from . import init_db
from typing import Optional
from fastapi import Header, HTTPException

from .modules import (
    get_user_repos, 
    get_user_commits, 
    save_repo_and_commits, 
    check_repo_update_needed,
    validate_date_n_token,
    get_total_commit_num, 
    get_specific_repo_commit_num
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "working!"}


@app.get("/save/{github_username}/all")
async def get_repo_n_commits_then_save_to_db(
    github_username: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    
    start_date, end_date = validate_date_n_token(github_username, year, month, github_token)

    # 레포 정보 가져오기
    repos = get_user_repos(github_token, start_date, end_date)
    
    if isinstance(repos, list):
        try:
            for repo in repos:
                # 레포 업데이트 필요 여부 확인
                if check_repo_update_needed(github_username, repo['name'], repo['updated_at']):
                    # 각 레포 커밋 정보 가져오기
                    commits = get_user_commits(github_token, github_username, repo['name'], start_date, end_date)
                    
                    if isinstance(commits, list):
                        # 데이터베이스에 저장
                        result = save_repo_and_commits(github_username, repo, commits)
                        print(f"Repository {repo['name']} updated: {result}")
                    else:
                        print(f"Error getting commits for {repo['name']}: {commits}")
                else:
                    print(f"Repository {repo['name']} is up to date, skipping...")
        finally:
            return {"success": True, "message": "done!"}
    else:
        return {"success": False, "message": "Error getting repositories"}


@app.get("/get/{github_username}/repo")
async def get_repository(
    github_username: str,
    year: Optional[int] = None, 
    month: Optional[int] = None,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    
    start_date, end_date = validate_date_n_token(github_username, year, month, github_token)

    # 해당 기간의 레포들 가져와서 바로 반환
    return get_user_repos(github_token, start_date, end_date)

@app.get("/save/{github_username}/specific")
async def save_specific_repo_n_commits_to_db(
    github_username: str,
    repository: Optional[dict] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    """
    return:
        success: boolean
        message: string
    """
    
    if repository is None:
        raise HTTPException(status_code=422, detail="Repository is required")

    start_date, end_date = validate_date_n_token(github_username, year, month, github_token)
    
    # 레포지토리 업데이트 필요 여부 확인 (true일 경우 업뎃 필요)
    if check_repo_update_needed(github_username, repository['name'], repository['updated_at']):
        # 해당 레포 커밋 정보 가져오기
        commits = get_user_commits(github_token, github_username, repository['name'], start_date, end_date)
        
        if isinstance(commits, list):
            # 데이터베이스에 저장
            result = save_repo_and_commits(github_username, repository, commits)
            return {"success": True, "message": f"'{repository['name']}' is saved! {result}"}
        else:
            return {"success": False, "message": f"Error getting commits for {repository['name']}: {commits}"}
    else:
        return {"success": True, "message": f"'{repository['name']}' is saved!"}

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