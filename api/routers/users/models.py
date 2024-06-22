import sys
from typing import Self
sys.path.append(".")

from pydantic import BaseModel, UUID4, Field, field_validator

from api.db.models.users import User

class UserResponseElement(BaseModel):
    id: UUID4
    username: str


class UserResponse(BaseModel):
    success: bool = True
    message: str | None = None
    user: UserResponseElement | None = None

    @staticmethod
    def set_by_user(user: User, message: str = None) -> Self:
        user = User.get_user_by_id(user.id)
        return UserResponse(
            message = message,
            user = UserResponseElement(
                id = user.id,
                username = user.username
            )
        )


class Username(BaseModel):
    name: str = Field(max_length=User.username.type.length, min_length=2)


class UserPassword(BaseModel):
    password: str = Field(min_length=8)

    @classmethod
    @field_validator('password')
    def validate_password(cls, value: str):
        if not any(char.isdigit() for char in value):
            raise ValueError('The password must contain a Numeric value')
        
        if not any(char.isupper() for char in value):
            raise ValueError('The password must contain a Upper case char')

        if not any(char.islower() for char in value):
            raise ValueError('The password must contain a Lower case char')
        
        if all(char.isalnum() for char in value):
            raise ValueError('The password must contain at least one non alpanumeric char')

        return value


class UserRequest(BaseModel):
    username: Username
    password: UserPassword
