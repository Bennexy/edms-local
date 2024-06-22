from pydantic import BaseModel, UUID4
from api.routers.users.models import Username, UserPassword

class TokenResponse(BaseModel):
    success: bool = True
    token: UUID4|str|None

class UserAuth(BaseModel):
    Username: Username
    password: UserPassword