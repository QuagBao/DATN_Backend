from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.schemas.response.role_response import RoleOut

class account_out(BaseModel):
    
    id_account: str
    email: str
    phone: Optional[str]
    full_name: Optional[str]
    status: Optional[str]
    role: Optional[RoleOut]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
