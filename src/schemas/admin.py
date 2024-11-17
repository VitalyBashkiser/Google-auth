from pydantic import BaseModel


class AdminResponse(BaseModel):
    message: str
    details: str | dict = None


class PermissionResponse(BaseModel):
    user_id: int
    permission: str
    message: str
    granted_at: str
