from sqlalchemy import text
try:
    from ..modules import validate_date_n_token
    from .. import SessionLocal
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from be import SessionLocal
    from be.modules import validate_date_n_token
from typing import List, Dict
from sqlalchemy.orm import Session

def get_user_commits(user: str, year: int, month: int, token: str) -> List[Dict]:
    """
    특정 사용자의 특정 월에 해당하는 커밋들을 db에서 얻어와요 << 속도 문제 있을지도...

    args:
        user_name, year, month, token
    
    return: List[Dict]
        [(commit_id, repo_id)]
    """

    db: Session = SessionLocal()

    start_date, end_date = validate_date_n_token(user, year, month, token)
    
    query = text("""
        SELECT 
            c.commit_id,
            c.repo_id
        FROM commits c
        WHERE c.author = :username
        AND c.commit_date BETWEEN :start_date AND :end_date
        ORDER BY c.commit_date DESC
    """)
    
    result = db.execute(query, {
        "username": user,
        "start_date": start_date,
        "end_date": end_date
    })
    
    return result.fetchall()

def create_human_prompt(commit_id: int, repo_id: int) -> str:
    """
    commit id랑 repo id 바탕으로 변경된 코드들 얻어와서 human prompt 만들어요
    """

    db: Session = SessionLocal()
    
    repo_query = text("""
        SELECT repo_name
        FROM repositories
        WHERE repo_id = :repo_id
    """)
    
    changes_query = text("""
        SELECT 
            c.commit_message,
            cc.file_path,
            cc.change_type,
            cc.content
        FROM commits c
        LEFT JOIN code_changes cc ON c.commit_id = cc.commit_id
        WHERE c.commit_id = :commit_id
        ORDER BY cc.file_path
    """)
    
    try:
        repo_result = db.execute(repo_query, {"repo_id": repo_id}).first()
        if not repo_result:
            return "Repository not found"
        
        changes_result = db.execute(changes_query, {"commit_id": commit_id}).fetchall()
        if not changes_result:
            return "No changes found for this commit"
        
        output = [f"- repository name: {repo_result.repo_name}\n"]
        output.append("- commit")
        
        output.append(f'\t- commit message: "{changes_result[0].commit_message}"')
        
        
        for change in changes_result:
            output.append(f"\t- changed file: {change.file_path}")
            output.append(f"\t\t- type: {change.change_type}")
            output.append(f"\t\t- content: '''\n{change.content}\n'''")
            output.append("") 
        
        return "\n".join(output)
        
    finally:
        db.close()

if __name__ == "__main__":
    import dotenv
    import os
    dotenv.load_dotenv()

    user: str = os.getenv("GITHUB_USER")
    token: str = os.getenv("GITHUB_TOKEN")

    print(get_user_commits(user, 2024, 11, token))
    print(create_human_prompt(1, 1))