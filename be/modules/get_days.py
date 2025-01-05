from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from . import validate_date_n_token
from ..models import Commit, Repository  # models 파일에서 필요한 모델들을 import 해야 합니다

def get_active_days(github_username: str, github_token: str, year: int, month: int, db: Session = SessionLocal()) -> List[str]:
    """
    github_username, github_token, year, month를 받아서 해당 기간동안 커밋된 날짜의 수를 반환
    """
    
    start_date, end_date = validate_date_n_token(github_username, year, month, github_token)
    
    # Repository와 Commit 테이블을 조인하여 해당 사용자의 커밋 날짜들을 조회
    active_days = db.query(
        func.count(distinct(func.date(Commit.commit_date))).label('active_days')
    ).join(
        Repository, Repository.repo_id == Commit.repo_id
    ).filter(
        Repository.github_username == github_username,
        Commit.commit_date >= start_date,
        Commit.commit_date <= end_date
    ).scalar() or 0
    
    total_days = (end_date - start_date).days + 1
    
    return active_days, total_days