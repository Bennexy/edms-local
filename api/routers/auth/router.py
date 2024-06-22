import sys
sys.path.append(".")

from fastapi import APIRouter, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from api.db.models.users import User
from logger import get_logger
from api.exceptions.base import ServerHTTPException
from api.routers.auth.models import TokenResponse

logger = get_logger()
security = HTTPBasic()
router = APIRouter(prefix="/oauth", tags=["oauth"])

@router.get("/token", response_model = TokenResponse)
async def get_token(
    credentials: HTTPBasicCredentials = Depends(security)
):
    user: User = User.get_user_by_username(credentials.username)

    if user.verify_password(credentials.password):
        return TokenResponse(token = user.generate_token())
    
    raise ServerHTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Invalid password"
    )
    
