import requests
from datetime import datetime
from icecream import ic
from typing import List, Dict
import os
import dotenv

dotenv.load_dotenv()


def get_user_repos(token: str, start_date: datetime, end_date: datetime) -> List[Dict] | tuple:
    """
    start_date, end_date 사이에 있는 모든 레포(레포이름, url, private유무, 최종업뎃날짜) 가져옴
    private 레포지토리도 포함
    
    params: Dict[str, str] = {
      'start_date': start_date.strftime('%Y-%m-%d'),
      'end_date': end_date.strftime('%Y-%m-%d')
    }
    
    return: List[Dict] | tuple
    """

    url: str = "https://api.github.com/user/repos"
    headers: Dict[str, str] = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    params: Dict[str, str] = {
        'visibility': 'all',  # public, private 모두 포함
        'sort': 'updated',
        'per_page': 100
    }
    
    response: requests.Response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        repos: List[Dict] = response.json()
        filtered_repos: List[Dict] = []
        for repo in repos:
            updated_at: datetime = datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            created_at: datetime = datetime.strptime(repo['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            
            if start_date <= updated_at <= end_date or start_date <= created_at <= end_date:
                filtered_repos.append(repo)
        return filtered_repos
    else:
        return (response.status_code, response.text)


if __name__ == "__main__":
    token: str = os.getenv("GITHUB_TOKEN")
    start_date: datetime = datetime(2024, 11, 1)
    end_date: datetime = datetime(2024, 12, 31)
    repos: List[Dict] | tuple = get_user_repos(token, start_date, end_date)

    if isinstance(repos, list):
        for repo in repos:
            repo_name: str = repo['name']
            repo_url: str = repo['html_url']
            is_private: bool = repo['private']
            updated_at: str = repo['updated_at']
            
            ic(repo_name, repo_url, is_private, updated_at)

