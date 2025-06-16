from pydantic import BaseModel
from typing import Optional

class ProjectIdeaRequest(BaseModel):
    id_account: str
    id_project: str
    description: str