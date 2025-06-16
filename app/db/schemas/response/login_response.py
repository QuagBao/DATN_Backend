# app/schemas/response/login_response.py
from pydantic import BaseModel
from app.db.schemas.response.account_response import account_out

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: account_out

    class Config:
        from_attributes = True