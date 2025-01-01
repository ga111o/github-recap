from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 데이터베이스 URL 설정 (비밀번호 변경)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:rootroot@localhost:5432/github_recap")

# 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

def init_db():
    try:
        # 데이터베이스 연결 확인
        with engine.connect() as conn:
            # 테이블 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS repositories (
                    repo_id SERIAL PRIMARY KEY,
                    github_username VARCHAR(255) NOT NULL,
                    repo_name VARCHAR(255) NOT NULL,
                    last_updated TIMESTAMP WITH TIME ZONE,
                    UNIQUE(github_username, repo_name)
                );

                CREATE TABLE IF NOT EXISTS commits (
                    commit_id SERIAL PRIMARY KEY,
                    repo_id INTEGER REFERENCES repositories(repo_id),
                    commit_hash VARCHAR(40) NOT NULL,
                    commit_message TEXT,
                    commit_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    UNIQUE(repo_id, commit_hash)
                );

                CREATE TABLE IF NOT EXISTS code_changes (
                    change_id SERIAL PRIMARY KEY,
                    commit_id INTEGER REFERENCES commits(commit_id),
                    file_path TEXT NOT NULL,
                    change_type VARCHAR(10) NOT NULL,
                    content TEXT
                );
            """))
            conn.commit()
    except Exception as e:
        print("===== error while init db =====")
        print(e)
        raise e
