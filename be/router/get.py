from fastapi import APIRouter, Header
from typing import Optional
from ..modules import (
    get_user_repos,
    get_total_commit_num,
    get_specific_repo_commit_num,
    validate_date_n_token,
    get_active_days,
    get_longest_streak,
    get_longest_gap,
    get_total_days,
    get_each_day_commit_count
)

router = APIRouter(prefix="/get")

@router.get("/{user}/repo/{year}/{month}")
async def get_repository(
    user: str,
    year: int, 
    month: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    
    start_date, end_date = validate_date_n_token(user, year, month, github_token)

    # 해당 기간의 레포들 가져와서 바로 반환
    return get_user_repos(github_token, start_date, end_date)

@router.get("/{user}/commit_num/total")
async def get_commit_num(
    user: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    return get_total_commit_num(github_token, user, year, month)

@router.get("/{user}/commit_num/specific")
async def get_commit_num(
    user: str,
    repo_name: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    return get_specific_repo_commit_num(github_token, user, repo_name, year, month)

@router.get("/{user}/used_language")
async def get_used_language(
    user: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    start_date, end_date = validate_date_n_token(user, year, month, github_token)

    return get_used_language(user, start_date, end_date)

@router.get("/{user}/days/active/{year}/{month}")
async def get_active_days_endpoint(
    user: str,
    year: int,
    month: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    active_days = get_active_days(user, github_token, year, month)
    return {"active_days": active_days}

@router.get("/{user}/days/longest_streak/{year}/{month}")
async def get_longest_streak_endpoint(
    user: str,
    year: int,
    month: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    longest_streak = get_longest_streak(user, github_token, year, month)
    return {"longest_streak": longest_streak}

@router.get("/{user}/days/longest_gap/{year}/{month}/{day}")
async def get_longest_gap_endpoint(
    user: str,
    year: int,
    month: int,
    day: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    longest_gap = get_longest_gap(user, github_token, year, month, day)
    return {"longest_gap": longest_gap}

@router.get("/days/total/{year}/{month}")
async def get_total_days_endpoint(
    year: int,
    month: int,
):
    total_days = get_total_days(year, month)
    return {"total_days": total_days}

@router.get("/{user}/days/each/{year}/{month}")
async def get_each_day_commit_count_endpoint(
    user: str,
    year: int,
    month: int,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    each_day_commit_count = get_each_day_commit_count(user, github_token, year, month)
    return {"each_day_commit_count": each_day_commit_count}