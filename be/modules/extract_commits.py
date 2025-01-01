import os
import dotenv
from .get_user_commits import get_user_commits
from .get_user_repos import get_user_repos
from typing import List, Dict
from datetime import datetime

dotenv.load_dotenv()

def extract_commits(token: str, user: str, start_date: datetime, end_date: datetime) -> List[Dict]:
    repos: List[Dict] | tuple = get_user_repos(token, start_date, end_date)

    if isinstance(repos, list ):
        for repo in repos:
            commits: List[Dict] = get_user_commits(token, user, repo['name'], start_date, end_date)
            print(commits)
    else:
        print(repos)
    
    return commits