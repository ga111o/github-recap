from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session
try:
    from . import validate_date_n_token
    from .. import SessionLocal
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from be import SessionLocal
    from be.modules import validate_date_n_token
from typing import Optional 

def get_total_commit_num(github_token: str, user: str, year: Optional[int], month: Optional[int]) -> int:
    """
    github_token, user, year, month를 받아서 커밋 수를 반환해요.
    """

    start_date, end_date = validate_date_n_token(year, month, github_token)
    
    db: Session = SessionLocal()
    try:
        query = text("""
            SELECT COUNT(DISTINCT c.commit_hash)
            FROM commits c
            JOIN repositories r ON c.repo_id = r.repo_id
            WHERE r.github_username = :username
            AND c.commit_date BETWEEN :start_date AND :end_date
            AND c.author = :username
        """)
        
        result = db.execute(query, {
            "username": user,
            "start_date": start_date,
            "end_date": end_date
        }).scalar()
        
        return result or 0
    finally:
        db.close()

def get_specific_repo_commit_num(github_token: str, user: str, repo_name: str, year: Optional[int], month: Optional[int]) -> int:
    """
    github_token, user, repo_name, year, month를 받아서 특정 레포의 커밋 수를 반환해요.
    """
    
    start_date, end_date = validate_date_n_token(year, month, github_token)

    db: Session = SessionLocal()
    try:
        query = text("""
            SELECT COUNT(DISTINCT c.commit_hash)
            FROM commits c
            JOIN repositories r ON c.repo_id = r.repo_id
            WHERE r.github_username = :username
            AND r.repo_name = :repo_name
            AND c.commit_date BETWEEN :start_date AND :end_date
            AND c.author = :username
        """)
        
        result = db.execute(query, {
            "username": user,
            "repo_name": repo_name,
            "start_date": start_date,
            "end_date": end_date
        }).scalar()
        
        return result or 0
    finally:
        db.close()