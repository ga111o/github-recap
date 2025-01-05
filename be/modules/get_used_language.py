from sqlalchemy import text
try:
    from .. import SessionLocal
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from be import SessionLocal
from typing import List, Tuple
from sqlalchemy.orm import Session

def get_used_languages(github_username: str, start_date: str, end_date: str, db: Session = SessionLocal()) -> List[Tuple[str, int]]:
    """
    특정 기간 동안 커밋된 확장자 빈도를 내림차순으로 반환
    
    params:
        github_username (str): GitHub 사용자명
        start_date (str): 시작 날짜 (YYYY-MM-DD 형식)
        end_date (str): 종료 날짜 (YYYY-MM-DD 형식)
        db (Session): SQLAlchemy session
        
    returns:
        list: [(language, count), ...] 형식의 언어 사용 통계
    """

    try:
        query = text("""
            SELECT cc.language, COUNT(*) as count
            FROM code_changes cc
            JOIN commits c ON cc.commit_id = c.commit_id
            JOIN repositories r ON c.repo_id = r.repo_id
            WHERE r.github_username = :username
            AND c.commit_date BETWEEN :start_date AND :end_date
            AND cc.language IS NOT NULL
            GROUP BY cc.language
            ORDER BY count DESC
        """)
        
        result = db.execute(query, {
            "username": github_username,
            "start_date": start_date,
            "end_date": end_date
        })
        
        return [(row.language, row.count) for row in result]
    
    finally:
        db.close()


if __name__ == "__main__":
    print(get_used_languages("ga111o", "2024-01-01", "2025-01-01"))