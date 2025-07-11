from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DonationCreate(BaseModel):
    account_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    project_id: str
    amount: float
    paytime: Optional[datetime] = None
    transaction_id: Optional[str] = None
