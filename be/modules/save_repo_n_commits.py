from datetime import datetime, timezone
try:
    from .. import SessionLocal
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from be import SessionLocal
from typing import List, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy import text

async def save_repo_and_commits(
    github_username: str,
    repo_data: Dict,
    commits_data: List[Dict]
) -> Union[bool, str]:
    """
    레포지토리 정보와 커밋 데이터를 데이터베이스에 저장

    params:
        github_username: GitHub 사용자 이름
        repo_data: 레포지토리 정보
        commits_data: 커밋 정보 리스트

    return:
        True: 성공
        str: 실패 시 에러 메시지
    """
    try:
        db: Session = SessionLocal()
        
        # 레포지토리 저장
        repo_query = text("""
            INSERT INTO repositories (github_username, repo_name, repo_url, last_updated, is_secret)
            VALUES (:username, :repo_name, :repo_url, :last_updated, :is_secret)
            ON CONFLICT (github_username, repo_url) 
            DO UPDATE SET last_updated = :last_updated, is_secret = :is_secret
            RETURNING repo_id
        """)
        
        result = db.execute(
            repo_query,
            {
                "username": github_username,
                "repo_name": repo_data['name'],
                "repo_url": repo_data['html_url'],
                "last_updated": repo_data['updated_at'],
                "is_secret": repo_data['private']
            }
        )
        repo_id = result.scalar()
        
        # 커밋 데이터 저장
        for commit in commits_data:
            # 커밋 기본 정보 저장
            commit_query = text("""
                INSERT INTO commits (repo_id, commit_hash, commit_message, commit_date, author)
                VALUES (:repo_id, :commit_hash, :commit_message, :commit_date, :author)
                ON CONFLICT (repo_id, commit_hash)
                DO UPDATE SET 
                    commit_message = :commit_message,
                    author = :author
                RETURNING commit_id
            """)
            
            result = db.execute(
                commit_query,
                {
                    "repo_id": repo_id,
                    "commit_hash": commit['sha'],
                    "commit_message": commit['commit_message'],
                    "commit_date": commit['date'],
                    "author": commit['author']
                }
            )
            commit_id = result.scalar()
            
            for file_change in commit['files_changed']:
                filename = file_change['filename']
                file_extension = 'none'
                if '.' in filename:
                    possible_extension = filename.split('.')[-1]
                    if len(possible_extension) <= 45: 
                        file_extension = possible_extension

                change_query = text("""
                    INSERT INTO code_changes (
                        commit_id, file_path, change_type, content,
                        additions, deletions, changes, language
                    )
                    VALUES (
                        :commit_id, :file_path, :change_type, :content,
                        :additions, :deletions, :changes, :language
                    )
                """)
                
                db.execute(
                    change_query,
                    {
                        "commit_id": commit_id,
                        "file_path": file_change['filename'],
                        "change_type": file_change['status'],
                        "content": file_change.get('patch', ''),
                        "additions": file_change['additions'],
                        "deletions": file_change['deletions'],
                        "changes": file_change['changes'],
                        "language": file_extension or "none"
                    }
                )
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        return "error: " + str(e)
    finally:
        db.close()

def check_repo_update_needed(github_username: str, repo_url: str, updated_at: Union[str, datetime], db: Session = SessionLocal()) -> bool:
    """
    db 날짜 기준으로 레포의 업데이트 필요 여부를 확인
    username - repo_url 기준

    db에 없으면 True
    가져온 것과 비교했을 때, db 값이 작으면 True

    return:
        True: 업데이트 필요
        False: 업데이트 불필요
    """
    try:
        query = text("""
            SELECT last_updated 
            FROM repositories 
            WHERE github_username = :username AND repo_url = :repo_url
        """)
        
        result = db.execute(query, {"username": github_username, "repo_url": repo_url})
        db_updated_at = result.scalar()
        
        if not db_updated_at:
            return True
        
        if isinstance(updated_at, str):
            github_updated_at = datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        else:
            github_updated_at = updated_at.replace(tzinfo=timezone.utc) if updated_at.tzinfo is None else updated_at
            
        return github_updated_at > db_updated_at
    finally:
        db.close()

if __name__ == "__main__":
    from get_user_repos import get_user_repos
    from get_user_commits import get_user_commits
    import os
    import dotenv
    
    dotenv.load_dotenv()
    
    token = os.getenv("GITHUB_TOKEN")
    github_username = os.getenv("GITHUB_USER")
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 1, 31)
    
    # 레포 정보 가져오기
    repos = get_user_repos(token, start_date, end_date)
    
    if isinstance(repos, list):
        try:
            db = SessionLocal() 
            for repo in repos:
                # check_repo_update_needed에 세션 전달
                if check_repo_update_needed(github_username, repo['name'], repo['updated_at'], db):
                    commits = get_user_commits(token, github_username, repo['name'], start_date, end_date)
                    
                    if isinstance(commits, list):
                        result = save_repo_and_commits(github_username, repo, commits)
                        print(f"{result}\t| Repository {repo['name']} updated")
                    else:
                        print(f"err     | Error getting commits for {repo['name']}: {commits}")
                else:
                    print(f"skip    | Repository {repo['name']} is up to date")
        finally:
            db.close()  
            print("done!")