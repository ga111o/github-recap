from fastapi import APIRouter, Header
from typing import Optional
from ..model import RequestBody
from ..modules import (
    check_repo_update_needed,
    get_user_commits,
    save_repo_and_commits,
    validate_date_n_token,
    get_latest_commit_sha
)

router = APIRouter()

@router.post("/save/{github_username}/specific/{year}/{month}")
async def save_specific_repo_n_commits_to_db(
    github_username: str,
    year: int,
    month: int,
    request_body: RequestBody,
    github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
):
    repository = request_body.repository.model_dump()
    start_date, end_date = validate_date_n_token(github_username, year, month, github_token)
    
    if check_repo_update_needed(github_username=github_username, repo_url=repository['html_url'], updated_at=repository['updated_at']):
        # DB에서 최신 커밋 SHA 가져오기
        latest_commit_sha = get_latest_commit_sha(github_username, repository['html_url']) 
        
        commits = get_user_commits(
            github_token, 
            github_username, 
            repository['name'], 
            start_date, 
            end_date,
            latest_commit_sha
        )
        
        if isinstance(commits, list):
            result = save_repo_and_commits(github_username, repository, commits)
            return {
                "success": True,
                "message": f"'{repository['name']}' is saved! {result}",
                "total_commits": len(commits)
            }
        else:
            return {
                "success": False,
                "message": f"Error getting commits for {repository['name']}: {commits}"
            }
    else:
        return {
            "success": True,
            "message": f"'{repository['name']}' is already up to date!"
        }