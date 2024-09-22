import sys
from typing import Self

import jwt
import uuid
import datetime
from fastapi import status
from sqlalchemy import (
    ARRAY,
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
from langdetect import detect
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import make_searchable, search
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import joinedload

sys.path.append(".")
from api.modules.language.languages import Languages
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

    id: UUID = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid.uuid4(),
    )
    file_id: UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("files.id"),
        nullable=False,
        index=True,
        unique=True,
    )
    user_id: UUID = Column(UUID(as_uuid=True), nullable=False, index=True)

    file_text: list[str] = Column(ARRAY(String), nullable=True)

    # Full-text search vector
    _search_vector = Column(
        TSVECTOR,
        name="search_vector",
        nullable=False,
    )

    @hybrid_property
    def search_vector(self):
        return self._search_vector

    @search_vector.expression
    def search_vector(cls):
        return func.to_tsvector("german", func.array_to_string(cls.file_text, " "))

    created_on: DateTime = Column(DateTime(), nullable=False, server_default=func.now())
    last_modified_on: DateTime = Column(DateTime(), nullable=True, onupdate=func.now())
    deleted_on: DateTime = Column(DateTime(), nullable=True)
    deleted: Boolean = Column(Boolean(), nullable=False, default=False)

    file: Mapped["Files"] = relationship(
        "Files",
        back_populates="file_text",
        lazy="noload",
        uselist=False,
    )

    @db
    @staticmethod
    def new(file_id: UUID, user: User, db: DB = DB) -> UUID:
        id = uuid.uuid4()
        file_text = FileText()

        file_text.id = id
        file_text.file_id = file_id
        file_text.user_id = user.id
        file_text.file_text = [""]
        file_text._search_vector = FileText.generate_ts_search_vector([""])

        db.add(file_text)
        db.commit()

        return id

    @classmethod
    def create(cls, file_id: UUID, user: User) -> Self:
        id = cls.new(file_id, user)

        return cls.get(id)

    @db
    @staticmethod
    def get(id: UUID, user: User, db: DB) -> "FileText":
        return (
            db.query(FileText)
            .filter(FileText.id == id, FileText.user_id == user.id)
            .first()
        )

    @db
    @staticmethod
    def get_by_file_id(id: UUID, user: User, db: DB) -> "FileText":
        return (
            db.query(FileText)
            .filter(FileText.file_id == id, FileText.user_id == user.id)
            .first()
        )

    @staticmethod
    def generate_ts_search_vector(text: list[str]) -> str:
        con = func.array_to_string(text, " ")
        return func.to_tsvector("german", con)

    @db
    @staticmethod
    def find_by_text(user: User, text: str, db: DB) -> list[Self]:
        res = list()
        for element in (
            db.query(FileText)
            .where(FileText.search_vector.match(text))
            .filter(FileText.user_id == user.id)
            .all()
        ):
            res.append(element)

        return res

    @db
    def save_file_text(self, text: list[str], db: DB = DB) -> Self:
        self.file_text = text
        self._search_vector = self.generate_ts_search_vector(text, self.language)
        db.add(self)
        db.commit()
        db.refresh(self)

        return self

    @db
    def delete(self, db: DB) -> Self:
        self.deleted = True
        self.deleted_on = datetime.datetime.now()

        db.add(self)
        db.commit()

        return self

    @staticmethod
    def detect_language(text):
        try:
            return detect(text)
        except Exception:
            return "english"  # Default to English if detection fails

    @staticmethod
    def get_tsvector_language(language_code):
        if language_code == "de":
            return "german"
        elif language_code == "en":
            return "english"
        else:
            return "english"  # Default to English


class Files(Base):
    __tablename__ = "files"

    id: UUID = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid.uuid4(),
    )
    user_id: UUID = Column(UUID(as_uuid=True), nullable=False, index=True, unique=False)

    filename: str = Column(String(length=255), nullable=False, index=True)
    language: Languages = Column(String(length=2), nullable=False, default="")
    # Will be added later in the project
    # document_type: Mapped[DocumentType] = relationship(
    #     "DocumentType",
    #     back_populates="file",
    #     lazy="selectin",
    #     uselist=False,
    # )

    created_on: DateTime = Column(DateTime(), nullable=False, server_default=func.now())
    last_modified_on: DateTime = Column(DateTime(), nullable=True, onupdate=func.now())
    deleted_on: DateTime = Column(DateTime(), nullable=True)
    deleted: Boolean = Column(Boolean(), nullable=False, default=False)

    file_text: Mapped[FileText] = relationship(
        "FileText",
        back_populates="file",
        lazy="selectin",
        uselist=False,
    )

    @classmethod
    @db
    def new(
        cls, user: User, filename: str, id: None | UUID = None, db: DB = None
    ) -> Self:
        if id is None:
            id = uuid.uuid4()

        file = cls()

        file.id = id
        file.user_id = user.id
        file.filename = filename

        db.add(file)
        db.commit()
        FileText.new(id, user)

        db.refresh(file)

        return file

    @db
    def get_without_text(user: User, id: UUID, db: DB) -> "Files":
        return db.query(Files).filter(Files.id == id, Files.user_id == user.id).first()

    @db
    @staticmethod
    def get_with_text(user: User, id: UUID, db: DB) -> "Files":
        return (
            db.query(Files)
            .options(joinedload(Files.file_text))
            .filter(Files.id == id, Files.user_id == user.id)
            .first()
        )

    @staticmethod
    def find_by_text(user: User, text: str) -> list[UUID]:
        return [file.id for file in FileText.find_by_text(user, text)]

    @db
    @staticmethod
    def list_all(user: User, db: DB) -> list["Files"]:
        return (
            db.query(Files)
            .options(joinedload(Files.file_text))
            .filter(Files.user_id == user.id)
            .all()
        )
