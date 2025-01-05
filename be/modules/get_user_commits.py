import requests
from datetime import datetime
from typing import List, Dict, Union
import os
import dotenv
from icecream import ic


dotenv.load_dotenv()

def get_user_commits(token: str, user: str, repo_name: str, start_date: datetime, end_date: datetime) -> Union[List[Dict], tuple]:
    """
    주어진 레포지토리 이름과 날짜 범위에 대한 커밋 정보, 변경된 파일들, 그리고 추가/삭제된 코드를 가져옴.

    params: 
      - token: GitHub API 접근을 위한 토큰
      - user: 유저 이름
      - repo_name: 레포 이름
      - start_date: 시작 날짜
      - end_date: 종료 날짜

    return: List[Dict] - 커밋 정보 리스트

    [
    {
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
              'patch': file.get('patch', '')
          } for file in commit_data['files']
      ]
  },
    ]
    """
    
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
            all_commits.extend(commits)
            
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                break
        else:
            return (response.status_code, response.text)


    detailed_commits = []
    for commit in all_commits:
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

if __name__ == "__main__":
    token: str = os.getenv("GITHUB_TOKEN")
    user: str = os.getenv("GITHUB_USER")
    repo_name: str = os.getenv("GITHUB_TEST_REPO")
    start_date: datetime = datetime(2025, 1, 1)  
    end_date: datetime = datetime(2025, 1, 31)  
    commits: Union[List[Dict], tuple] = get_user_commits(token, user, repo_name, start_date, end_date)

    ic(commits)
