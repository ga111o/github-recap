from sqlalchemy.orm import Session
from sqlalchemy import text
from .. import SessionLocal

def save_llm_output(user: str, repo_id: int, year: int, month: int, content: str):
    db: Session = SessionLocal()
    try:
        query = text("""
            INSERT INTO repo_recaps (github_username, repo_id, year, month, content)
            VALUES (:user, :repo_id, :year, :month, :content)
            ON CONFLICT (github_username, repo_id, year, month)
            DO UPDATE SET 
                content = :content,
                updated_at = CURRENT_TIMESTAMP
        """)
        
        db.execute(query, {
            "user": user,
            "repo_id": repo_id,
            "year": year,
            "month": month,
            "content": content
        })
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
