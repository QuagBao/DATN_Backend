from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DonationCreate(BaseModel):
    account_id: str
    project_id: str
    amount: float
    paytime: Optional[datetime] = None
    transaction_id: Optional[str] = None