from pydantic import BaseModel

class RoleOut(BaseModel):
    id_role: int
    name: str