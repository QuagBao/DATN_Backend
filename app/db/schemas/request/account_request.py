from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Dùng cho /register
class account_create(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: str
    password: str
    
# Dùng cho /login
class account_login(BaseModel):
    email: str #vẫn là email nha
    password: str
    
class account(BaseModel):
    id: str
    email: str
    password: str
    
class admin_update(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    
class staff_update(BaseModel):
    full_name: Optional[str]
    phone: Optional[str]
    password: Optional[str]
    
class user_update(BaseModel):
    full_name: Optional[str]
    phone: Optional[str]
    password: Optional[str]