import sys
from typing import Self

import jwt
import uuid
import datetime
from fastapi import status
from sqlalchemy import (
    Column,
    UUID,
    Index,
    String,
    DateTime,
    Boolean,
    Text,
    func,
    ForeignKey,
    RowMapping,
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import make_searchable, search
from werkzeug.security import check_password_hash, generate_password_hash


sys.path.append(".")
from logger import get_logger
from api.config import SECRET_KEY
from api.db.database import db, DB, Base
from api.db.models.users import User
from api.exceptions.db import ServerDBException
from api.exceptions.base import ServerHTTPException

logger = get_logger()


class FileText(Base):
    __tablename__ = "file_text"
    # enable full text seach on the file_text
    __table_args__ = (
        Index("ix_file_search_vector", "search_vector", postgresql_using="gin"),
    )

    id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid.uuid4(),
    )
    file_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("files.id"),
        nullable=False,
        index=True,
        unique=True,
    )

    file_text: Mapped[str] = Column(Text, nullable=True)

    # Full-text search vector
    search_vector: Mapped[str] = Column(TSVectorType("file_text"))

    created_on: Mapped[DateTime] = Column(
        DateTime(), nullable=False, server_default=func.now()
    )
    last_modified_on: Mapped[DateTime] = Column(
        DateTime(), nullable=True, onupdate=func.now()
    )
    deleted_on: Mapped[DateTime] = Column(DateTime(), nullable=True)
    deleted: Mapped[Boolean] = Column(Boolean(), nullable=False, default=False)

    file: Mapped["Files"] = relationship(
        "Files",
        back_populates="file_text",
        lazy="noload",
        uselist=False,
    )

    @db
    @staticmethod
    def new(file_id: UUID, db: DB, file_text: str | None = None) -> UUID:
        id = uuid.uuid4()
        file_text = FileText()

        file_text.id = id
        file_text.file_id = file_id
        file_text.file_text = file_text

        db.add(file_text)
        db.commit()

        return id

    @db
    def delete(self, db: DB) -> Self:
        self.deleted = True
        self.deleted_on = datetime.datetime.now()

        db.add(self)
        db.commit()

        return self


class Files(Base):
    __tablename__ = "files"

    id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid.uuid4(),
    )
    user_id: Mapped[UUID] = Column(
        UUID(as_uuid=True), nullable=False, index=True, unique=False
    )

    filename: Mapped[str] = Column(String(length=255), nullable=False, index=True)

    created_on: Mapped[DateTime] = Column(
        DateTime(), nullable=False, server_default=func.now()
    )
    last_modified_on: Mapped[DateTime] = Column(
        DateTime(), nullable=True, onupdate=func.now()
    )
    deleted_on: Mapped[DateTime] = Column(DateTime(), nullable=True)
    deleted: Mapped[Boolean] = Column(Boolean(), nullable=False, default=False)

    file_text: Mapped[FileText] = relationship(
        "FileText",
        back_populates="file",
        lazy="selectin",
        uselist=False,
    )

    @staticmethod
    def new(user: User, filename: str, id: None | UUID = None, db: DB = None) -> UUID:
        if id is None:
            id = uuid.uuid4()

        file = Files()

        file.id = id
        file.user_id = user.id
        file.filename = filename

        file.file_text_id = FileText.new(id, db=db, file_text=None)

        db.add(file)
        db.commit()

        return id

    @db
    def get_without_text(user: User, id: UUID, db: DB) -> "Files":
        db.query(Files).filter(Files.id == id, Files.user == user)
