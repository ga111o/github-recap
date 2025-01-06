from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from . import validate_date_n_token
from .. import SessionLocal
from sqlalchemy.sql import text


def get_active_days(github_username: str, github_token: str, year: int, month: int) -> List[str]:
    """
    github_username, github_token, year, month를 받아서 해당 기간동안 커밋된 날짜의 수를 반환
    Returns:
        tuple: (active_days, total_days)
        - active_days: 실제로 커밋한 날짜 수
        - total_days: 해당 월의 총 일수
    """
    db = SessionLocal()
    try:
        start_date, end_date = validate_date_n_token(github_username, year, month, github_token)

        # 활성 날짜 수 계산 (중복 제거된 날짜 수)
        active_days_query = db.execute(text("""
            SELECT COUNT(DISTINCT DATE(c.commit_date))
            FROM commits c
            JOIN repositories r ON c.repo_id = r.repo_id
            WHERE r.github_username = :username
            AND c.commit_date >= :start_date
            AND c.commit_date < :end_date
        """), {
            "username": github_username,
            "start_date": start_date,
            "end_date": end_date
        })
        active_days = active_days_query.scalar() or 0

        # 해당 달의 총 일수 (total days) 계산
        total_days_query = db.execute(text("""
            SELECT DATE_PART('days', 
                DATE_TRUNC('month', :end_date) - 
                DATE_TRUNC('month', :start_date)
            )::integer
        """), {
            "start_date": start_date,
            "end_date": end_date
        })
        total_days = total_days_query.scalar()
        
        return active_days, total_days
    
    except Exception as e:
        raise Exception(f"get active days err: {str(e)}")
    
    finally:
        db.close()