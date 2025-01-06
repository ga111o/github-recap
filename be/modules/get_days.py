from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
try:
    from . import validate_date_n_token
    from .. import SessionLocal
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from be import SessionLocal
    from be.modules import validate_date_n_token
from datetime import datetime
from sqlalchemy.sql import text
from icecream import ic

def get_total_days(db: Session, start_date: datetime) -> int:
    """
    Calculate total days in a month for a given start date
    Returns:
        int: Total number of days in the month
    """
    total_days_query = db.execute(text("""
        SELECT EXTRACT(DAY FROM 
            (DATE_TRUNC('month', :start_date) + INTERVAL '1 month - 1 day')::date
        )::integer
    """), {
        "start_date": start_date
    })
    return total_days_query.scalar()

def get_active_days(github_username: str, github_token: str, year: int, month: int) -> Tuple[int, int]:
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
        ic(start_date, end_date)

        active_days = len(get_each_day_commit_count(github_username, github_token, year, month))
        total_days = get_total_days(db, start_date)
        
        return active_days, total_days
    
    except Exception as e:
        raise Exception(f"get active days err: {str(e)}")
    
    finally:
        db.close()

def get_longest_streak(github_username: str, github_token: str, year: int, month: int) -> Tuple[int, int]:
    """
    github_username, github_token, year, month를 받아서 해당 기간동안 가장 긴 연속 커밋 기간을 반환
    Returns:
        tuple: (longest_streak, total_days)
        - longest_streak: 가장 긴 연속 커밋 기간
        - total_days: 해당 월의 총 일수
    """

    db = SessionLocal()
    try:
        start_date, end_date = validate_date_n_token(github_username, year, month, github_token)

        # 해당 기간의 모든 커밋 날짜 가져오기 (time zone seoul 조심)
        dates_query = db.execute(text("""
            SELECT DISTINCT DATE(c.commit_date AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul') as commit_date
            FROM commits c
            JOIN repositories r ON c.repo_id = r.repo_id
            WHERE r.github_username = :username
            AND c.commit_date >= :start_date
            AND c.commit_date < :end_date
            ORDER BY commit_date
        """), {
            "username": github_username,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # 커밋된 날짜들을 리스트로 변환
        commit_dates = [row[0] for row in dates_query]

        longest_streak = 0
        current_streak = 0
        
        if commit_dates:
            current_streak = 1
            for i in range(1, len(commit_dates)):
                # 이전 날짜와 현재 날짜의 차이가 1일이면 연속된 커밋으로
                if (commit_dates[i] - commit_dates[i-1]).days == 1:
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1
            
            # 마지막 streak 확인
            longest_streak = max(longest_streak, current_streak)

        total_days = get_total_days(db, start_date)
        return longest_streak, total_days

    except Exception as e:
        raise Exception(f"get longest streak err: {str(e)}")
    
    finally:
        db.close()

def get_longest_gap(github_username: str, github_token: str, year: int, month: int, day: int) -> Tuple[int, int]:
    """
    github_username, github_token, year, month, day를 받아서 1일부터 현재까지 가장 길게 커밋하지 않은 연속된 날짜의 수를 반환
    Returns:
        tuple: (longest_gap, total_days)
        - longest_gap: 가장 긴 연속으로 커밋을 하지 않은 기간
        - total_days: 해당 월의 총 일수
    """
    db = SessionLocal()
    try:
        start_date, _ = validate_date_n_token(github_username, year, month, github_token)
        # 주어진 day로 현재 날짜 만들기
        end_date = datetime(year, month, day) 

        # 주어진 기간 동안 모든 커밋 날짜 가져오기
        dates_query = db.execute(text("""
            SELECT DISTINCT DATE(c.commit_date AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul') as commit_date
            FROM commits c
            JOIN repositories r ON c.repo_id = r.repo_id
            WHERE r.github_username = :username
            AND c.commit_date >= :start_date
            AND c.commit_date < :end_date
            ORDER BY commit_date
        """), {
            "username": github_username,
            "start_date": start_date,
            "end_date": end_date
        })
        
        commit_dates = [row[0] for row in dates_query]
        longest_gap = 0
        
        if commit_dates:
            # 지정된 날짜까지의 커밋 날짜 필터링
            commit_dates = [d for d in commit_dates if d < end_date.date()]
            
            if not commit_dates:
                # 지정된 날짜까지 커밋이 없는 경우
                longest_gap = (end_date.date() - start_date.date()).days - 1
            else:
                # 월의 시작부터 첫 커밋까지의 간격 확인
                if (commit_dates[0] - start_date.date()).days > longest_gap:
                    longest_gap = (commit_dates[0] - start_date.date()).days
                
                # 커밋 간의 간격 확인
                for i in range(1, len(commit_dates)):
                    gap = (commit_dates[i] - commit_dates[i-1]).days - 1
                    longest_gap = max(longest_gap, gap)
                
                # 마지막 커밋부터 지정된 날짜까지의 간격 확인
                if (end_date.date() - commit_dates[-1]).days - 1 > longest_gap:
                    longest_gap = (end_date.date() - commit_dates[-1]).days - 1
        else:
            # 커밋이 없는 경우, 시작부터 지정된 날짜까지의 간격으로
            longest_gap = (end_date.date() - start_date.date()).days - 1

        total_days = get_total_days(db, start_date)
        return longest_gap, total_days

    except Exception as e:
        raise Exception(f"get longest gap err: {str(e)}")
    
    finally:
        db.close()

def get_each_day_commit_count(github_username: str, github_token: str, year: int, month: int) -> List[Tuple[str, str, int]]:
    """
    github_username, github_token, year, month를 받아서 해당 기간동안 각 날짜별 레포의 커밋 수를 반환
    Returns:
        list: [(date, repo_name, commit_count)]
        - date: 날짜 (YYYY-MM-DD)
        - repo_name: 레포 이름
        - commit_count: 해당 날짜의 커밋 수
    """
    db = SessionLocal()
    try:
        start_date, end_date = validate_date_n_token(github_username, year, month, github_token)

        # 레포별 커밋 수 조회
        results = db.execute(text("""
            SELECT 
                DATE(c.commit_date AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul') as commit_date,
                r.repo_name,
                COUNT(*) as commit_count
            FROM commits c
            JOIN repositories r ON c.repo_id = r.repo_id
            WHERE r.github_username = :username
            AND c.commit_date >= :start_date
            AND c.commit_date < :end_date
            GROUP BY DATE(c.commit_date AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Seoul'), r.repo_name
            ORDER BY commit_date, r.repo_name
        """), {
            "username": github_username,
            "start_date": start_date,
            "end_date": end_date
        })

        # 튜플 (date, repo_name, commit_count)로 구성된 리스트로 변환
        return [(str(row[0]), row[1], row[2]) for row in results]

    except Exception as e:
        raise Exception(f"get each day commit count err: {str(e)}")
    
    finally:
        db.close()




if __name__ == "__main__":
    import os
    import dotenv
    dotenv.load_dotenv()
    
    token = os.getenv("GITHUB_TOKEN")
    github_username = os.getenv("GITHUB_USER")

    ic(get_active_days(github_username, token, 2025, 1))
    ic(get_longest_streak(github_username, token, 2025, 1))
    ic(get_longest_gap(github_username, token, 2025, 1, 6))
    ic(get_each_day_commit_count(github_username, token, 2025, 1))