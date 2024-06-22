import sys

import jwt
import uuid
import datetime
from fastapi import status
from sqlalchemy import Column, UUID, String, DateTime, Boolean, func
from werkzeug.security import check_password_hash, generate_password_hash


sys.path.append(".")
from logger import get_logger
from api.config import SECRET_KEY
from api.db.database import db, DB, Base
from api.exceptions.db import ServerDBException
from api.exceptions.base import ServerHTTPException

logger = get_logger()

class User(Base):
    __tablename__ = "users"

    id: Column[UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, unique=True, default=uuid.uuid4())
    username: Column[String] = Column(String(255), nullable=False, index=True, unique=True)
    password_hash = Column(String(255), nullable=False, index=True)

    
    created_on: Column[DateTime] = Column(DateTime(), nullable=False, server_default=func.now())
    last_modified_on: Column[DateTime] = Column(DateTime(), nullable=True, onupdate=func.now())
    deleted_on: Column[DateTime] = Column(DateTime(), nullable=True)
    deleted: Column[Boolean] = Column(Boolean(), nullable=False, default=False)


    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    

    @db
    @staticmethod
    def new(username: str, password: str, db: DB) -> UUID:

        if User.username_present(username):
            raise ServerHTTPException(status.HTTP_400_BAD_REQUEST, detail="User with this username is allready present")
        
        user = User()
        user.id = uuid.uuid4()
        user.username = username
        user.password_hash = generate_password_hash(password)

        db.add(user)
        db.commit()

        return user.id

    @db
    @staticmethod
    def username_present(username: str, db: DB) -> bool:
        user: User | None = db.query(User).filter(User.username == username).first()

        return user is not None
    
    @db
    @staticmethod
    def update_username_by_id(id: UUID, username: str, db: DB) -> "User":
        user = User.get_user_by_id(id, db=db)
        user.username = username

        db.add(user)
        db.commit()

        return user

    @db
    @staticmethod
    def get_user_by_token(token: str, db: DB) -> "User":
        user: User = db.query(User).filter(User.id == token).first()

        if user is None:
            raise ServerHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='No user found via the given token'
            )

        return user
    
    @db
    @staticmethod
    def get_user_by_id(id: uuid.UUID, db) -> "User":
        user: User = db.query(User).filter(User.id == id).first()

        if user is None:
            raise ServerDBException(
                'No user found with the id', {}, User
            )

        return user
    
    @db
    @staticmethod
    def get_user_by_username(username: str, db):
        user = db.query(User).filter(User.username == username).first()
        
        if user is None:
            raise ServerHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='No user found with this username'
            )

        return user
    
    @db
    def delete(self, db: DB):
        self.deleted = True
        self.deleted_on = datetime.datetime.now()
        db.commit()

    @db
    def update_password(self, password: str, db: DB):

        self.password = generate_password_hash(password)
        db.add(self)
        db.commit()

    def generate_token(self, expires_in=3600) -> str:
        
        return jwt.encode(
            {
                "confirm": str(self.id),
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=expires_in)
            },
            SECRET_KEY,
            algorithm="HS256"
        )

    @staticmethod
    def verify_auth_token(token) -> uuid.UUID|bool:
        if len(token) == 0:
            return False
        try:
            data: dict = jwt.decode(
                token,
                SECRET_KEY,
                leeway=datetime.timedelta(seconds=10),
                algorithms=["HS256"]
            )
            user_id = uuid.UUID(data.get('confirm'))
            User.get_user_by_id(user_id)
            return user_id

        except jwt.ExpiredSignatureError as ex:
            logger.error(ex)
            raise ServerHTTPException(403, {"sucess": False, "message": "The token is expired"}, exception=ex)
        
        except jwt.PyJWTError as ex:
            logger.error(ex)
            raise ServerHTTPException(403, {"sucess": False, "message": "The token is invalid"}, exception=ex)



