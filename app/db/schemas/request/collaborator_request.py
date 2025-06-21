from pydantic import BaseModel
from typing import Optional

class CollaboratorRequest(BaseModel):
    project_id: Optional[str] = None
    account_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    