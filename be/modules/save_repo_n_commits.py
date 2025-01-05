import sys
from pathlib import Path
from datetime import datetime, timezone

root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from be.database import SessionLocal
from typing import List, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy import text

def save_repo_and_commits(
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
            INSERT INTO repositories (github_username, repo_name, last_updated, is_secret)
            VALUES (:username, :repo_name, :last_updated, :is_secret)
            ON CONFLICT (github_username, repo_name) 
            DO UPDATE SET last_updated = :last_updated, is_secret = :is_secret
            RETURNING repo_id
        """)
        
        result = db.execute(
            repo_query,
            {
                "username": github_username,
                "repo_name": repo_data['name'],
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
            
            # 파일 변경 정보 저장
            for file_change in commit['files_changed']:
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
                        "language": file_change['language']
                    }
                )
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        return str(e)
    finally:
        db.close()

def check_repo_update_needed(db: Session, github_username: str, repo_name: str, updated_at: str) -> bool:
    """
    db 날짜 기준으로 레포지토리의 업데이트 필요 여부를 확인
    
    return:
        True: 업데이트 필요
        False: 업데이트 불필요
    """
    query = text("""
        SELECT last_updated 
        FROM repositories 
        WHERE github_username = :username AND repo_name = :repo_name
    """)
    
    result = db.execute(query, {"username": github_username, "repo_name": repo_name})
    db_updated_at = result.scalar()
    
    if not db_updated_at:
        return True
    
    # Convert GitHub timestamp to timezone-aware datetime
    github_updated_at = datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    return github_updated_at > db_updated_at

if __name__ == "__main__":
    from get_user_repos import get_user_repos
    from get_user_commits import get_user_commits
    import os
    import dotenv
    
    dotenv.load_dotenv()
    
    token = os.getenv("GITHUB_TOKEN")
    github_username = os.getenv("GITHUB_USER")
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # 레포 정보 가져오기
    repos = get_user_repos(token, start_date, end_date)
    
    if isinstance(repos, list):
        db = SessionLocal()
        try:
            for repo in repos:
                # 레포 업데이트 필요 여부 확인
                if check_repo_update_needed(db, github_username, repo['name'], repo['updated_at']):
                    # 각 레포 커밋 정보 가져오기
                    commits = get_user_commits(token, github_username, repo['name'], start_date, end_date)
                    
                    if isinstance(commits, list):
                        # 데이터베이스에 저장
                        result = save_repo_and_commits(github_username, repo, commits)
                        print(f"Repository {repo['name']} updated: {result}")
                    else:
                        print(f"Error getting commits for {repo['name']}: {commits}")
                else:
                    print(f"Repository {repo['name']} is up to date, skipping...")
        finally:
            db.close()
    else:
        print(f"Error getting repositories: {repos}")
