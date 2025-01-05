from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Optional
import requests

def validate_date_n_token(github_username: Optional[str], year: Optional[int], month: Optional[int], token: Optional[str]) -> bool:
    """
    date와 token을 정상적으로 받았는지 확인하고, 이상하다고 하면 함수 내에서 raise HTTPException을 해줘요.

    정상적인 값이면 start_date, end_date로 만들어서 각각 반환해요.
    """

    if github_username is None:
        raise HTTPException(status_code=422, detail="Github username is required")

    if token is None:
        raise HTTPException(status_code=422, detail="GitHub token must be provided")

    if year is None or month is None:
        raise HTTPException(status_code=422, detail="Year, month and GitHub ID must be provided")

    current_year = datetime.now().year

    if year < 2005 or year > current_year or month < 1 or month > 12:
        raise HTTPException(status_code=422, detail="Invalid year or month")

    start_date = datetime(year, month, 1)
    end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    url = "https://api.github.com/user"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        if user_info['login'] != github_username:
            raise HTTPException(status_code=422, detail="Github username is invalid")
        else:
            return start_date, end_date
        
    elif response.status_code == 401:
        raise HTTPException(status_code=422, detail="GitHub token is invalid or expired")
    else:
        raise HTTPException(status_code=422, detail="Unexpected Github API error")
