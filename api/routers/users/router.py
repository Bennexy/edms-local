import sys
sys.path.append(".")

from fastapi import APIRouter, Form, Depends

from api.db.models.users import User
from api import validate_token
from api.routers.users.models import UserResponse, UserRequest, Username, UserPassword

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create", response_model=UserResponse)
async def create_user(
    name: Username = Depends(Username),
    password: UserPassword = Depends(UserPassword)
):
    user: User = User.get_user_by_id(User.new(name.name, password.password))
    return UserResponse.set_by_user(user)


@router.get("/get_data", response_model=UserResponse)
async def get_user_data(user: User = Depends(validate_token)):
    return UserResponse.set_by_user(user)

@router.put("/update_username", response_model=UserResponse)
async def update_username(
    name: Username = Depends(Username), 
    user: User = Depends(validate_token)
):
    User.update_username_by_id(user.id, name.name)
    return UserResponse.set_by_user(user, 'Updated username')

@router.put("/update_password", response_model=UserResponse)
async def update_password(
    password: UserPassword = Depends(UserPassword), 
    user: User = Depends(validate_token)
):
    User.update_password_by_id(user.id, password.password)
    return UserResponse.set_by_user(user, 'Updated password')

@router.delete("/delete", response_model=UserResponse)
async def delete_user(user: User = Depends(validate_token)):
    User.delete_by_id(user.id)
    return UserResponse.set_by_user(user)
