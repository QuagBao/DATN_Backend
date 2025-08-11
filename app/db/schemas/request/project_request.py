from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional

class project_create(BaseModel):
    name_project: str
    content: str
    description: str
    start_date: str
    end_date: str
    total_numeric: float

class project_update(BaseModel):
    name_project: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_numeric: Optional[float] = None
