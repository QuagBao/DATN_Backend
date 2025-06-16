from pydantic import BaseModel
from datetime import date
from typing import Optional
from datetime import datetime
from app.db.schemas.response.image_response import ImageResponse

class ProjectOut(BaseModel):
    id_project: str
    name_project: str
    description: Optional[str]
    content: Optional[str]
    start_date: date
    end_date: date
    current_numeric: float
    total_numeric: float
    status: str
    images : list[ImageResponse]
    created_at: datetime
    updated_at: datetime
    

    class Config:
        from_attributes = True


class ProjectWithStats(ProjectOut):
    total_collaborators: int
    total_donors: int