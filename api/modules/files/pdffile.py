import os
import sys
from pathlib import Path
from typing import Self

from fastapi import UploadFile
from sqlalchemy import UUID

from api.db.models.users import User
from api.exceptions.file import InvalidFileFormatException

sys.path.append(".")
from api.db.models.files import Files as FilesDB
from api.config import BASE_FILE_DIR


class PDFFile:
    path: Path
    file: UploadFile
    db_file: FilesDB
    _bytes: bytes

    def __init__(self, file: UploadFile, filedb: FilesDB) -> None:
        self.path: Path = Path(BASE_FILE_DIR, filedb.id)
        self.file: UploadFile = file
        self.db_file = FilesDB

    @classmethod
    def new(cls, user: User, file: UploadFile) -> Self:
        if PDFFile.is_pdf_file(file) is False:
            raise InvalidFileFormatException(file, "musst be a pdf!")
        
        db_file = FilesDB.new(user, file.filename)

        file = PDFFile(file, db_file)

        return file


    @classmethod
    def load(cls, user: User, file_id: UUID) -> Self:
        PDFFile.load_with_db(FilesDB.get_without_text(user, file_id))

    @classmethod
    def load_with_db(cls, filedb: FilesDB) -> Self:
        file = cls()

        file.db_file = filedb
        file.path = Path(BASE_FILE_DIR, filedb.id).read_bytes()
        file.file = UploadFile(file.path.read_bytes())

        return file

    @property
    def bytes(self) -> bytes:
        if self._bytes is None:
            self._bytes = self.path.read_bytes()

        return self._bytes

    @property
    def text(self) -> str:
        return self.path.read_text("utf-8")

    @staticmethod
    def is_pdf_file(file: UploadFile) -> bool:
        return file.filename.lower().endswith(".pdf")

    def save(self):
        self.path.write_bytes(self.bytes)

    def delete(self):
        os.remove(self.path)
