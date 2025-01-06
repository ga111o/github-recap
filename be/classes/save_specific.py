from pydantic import BaseModel
from datetime import datetime

class Repository(BaseModel):
    name: str
    html_url: str
    private: bool
    updated_at: datetime

class RequestBody(BaseModel):
    repository: Repository
