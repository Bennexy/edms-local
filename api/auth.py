import sys
from uuid import UUID

sys.path.append(".")

from fastapi import Security, status
from fastapi.security.api_key import APIKeyHeader

from api.db.models.users import User
from api.exceptions.base import ServerHTTPException
from api.config import DEV_MODE

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def validate_token(auth_key_header: str = Security(api_key_header)) -> User:
    if DEV_MODE:
        return User.get_user_by_id(UUID("2e6f79c7-fa36-4f72-8321-c608ca4f2e30"))

    if auth_key_header is None:
        raise ServerHTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No Key passed"
        )

    user_id = User.verify_auth_token(auth_key_header)
    user = User.get_user_by_id(user_id)
    if user is None:
        raise ServerHTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Key"
        )

    return user
