import requests
from datetime import datetime
from typing import List, Dict, Union
import os
import dotenv
from icecream import ic
from .. import SessionLocal
from sqlalchemy import text


dotenv.load_dotenv()

def get_user_commits(token: str, user: str, repo_name: str, start_date: datetime, end_date: datetime, latest_commit_sha: str = None) -> Union[List[Dict], tuple]:
    """
    주어진 레포지토리 이름과 날짜 범위에 대한 커밋 정보를 가져옴.
    latest_commit_sha가 제공되면, 해당 커밋 이후의 새로운 커밋만 가져옴.

    params:
      - latest_commit_sha: DB에 저장된 가장 최근 커밋의 SHA (None이면 모든 커밋을 가져옴)
    """
    print(f"        | repository: {repo_name}, get commits")

    url: str = f"https://api.github.com/repos/{user}/{repo_name}/commits"
    headers: Dict[str, str] = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    params: Dict[str, str] = {
        'since': start_date.isoformat(),
        'until': end_date.isoformat(),
        'per_page': 100
    }
    
    all_commits: List[Dict] = []
    
    while True:
        response: requests.Response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            commits: List[Dict] = response.json()
            
            # 최신 커밋을 찾았거나 더 이상의 커밋이 없으면 중단
            if latest_commit_sha:
                for commit in commits:
                    if commit['sha'] == latest_commit_sha:
                        break
                new_commits = [c for c in commits if c['sha'] != latest_commit_sha]
                all_commits.extend(new_commits)
                break
            else:
                all_commits.extend(commits)
            
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                break
        else:
            return (response.status_code, response.text)

    detailed_commits = []
    for i, commit in enumerate(all_commits, 1):
        print(f"        | Fetching details for commit {i}/{len(all_commits)}: {commit['sha'][:7]}")
            
        commit_url = f"https://api.github.com/repos/{user}/{repo_name}/commits/{commit['sha']}"
        commit_response = requests.get(commit_url, headers=headers)
        if commit_response.status_code == 200:
            commit_data = commit_response.json()
            detailed_commits.append({
                'sha': commit['sha'],
                'commit_message': commit['commit']['message'],
                'author': commit['commit']['author']['name'],
                'date': commit['commit']['author']['date'],
                'files_changed': [
                    {
                        'filename': file['filename'],
                        'status': file['status'],
                        'additions': file['additions'],
                        'deletions': file['deletions'],
                        'changes': file['changes'],
                        'patch': file.get('patch', ''),
                        'language': os.path.splitext(file['filename'])[1].lower() or 'none'
                    } for file in commit_data['files']
                ]
            })
        else:
            return (commit_response.status_code, commit_response.text)
    
    return detailed_commits

def get_latest_commit_sha(user: str, repo_url: str) -> str:
    """
    DB에서 특정 레포의 가장 최근 커밋 SHA를 가져옴

    args:
        user (str)
        repo_url (str)

    return:
        str: 가장 최근 커밋의 SHA. 커밋이 없으면 None 반환
    """
    with SessionLocal() as session:
        query = text("""
            SELECT c.commit_hash
            FROM commits c
            JOIN repositories r ON c.repo_id = r.repo_id
            WHERE r.github_username = :username 
            AND r.repo_url = :repo_url
            ORDER BY c.commit_date DESC
            LIMIT 1
        """)
        
        result = session.execute(query, {
            "username": user,
            "repo_url": repo_url
        }).first()
        
        return result[0] if result else None

if __name__ == "__main__":
    token: str = os.getenv("GITHUB_TOKEN")
    user: str = os.getenv("GITHUB_USER")
    repo_name: str = os.getenv("GITHUB_TEST_REPO")
    start_date: datetime = datetime(2025, 1, 1)  
    end_date: datetime = datetime(2025, 1, 31)  
    commits: Union[List[Dict], tuple] = get_user_commits(token, user, repo_name, start_date, end_date)

    ic(commits)
