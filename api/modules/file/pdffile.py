import os
import shutil
import sys
from pathlib import Path
from typing import Self

from fastapi import UploadFile
from sqlalchemy import UUID

from api.db.models.users import User
from api.exceptions.file import (
    InvalidFileFormatException,
    InvalidFileOcrStatusException,
)

sys.path.append(".")
from api.db.models.files import Files as FilesDB, FileText as FileTextDB
from api.config import BASE_FILE_DIR
from api.modules.ocr.ocr import ocr_pdf, extract_text_from_pdf


class PDFFile:
    path: Path
    file: UploadFile
    db_file: FilesDB
    _bytes: bytes = None
    _ocr_path: Path = None

    def __init__(self, file: UploadFile, filedb: FilesDB) -> None:
        self.path: Path = Path(BASE_FILE_DIR, str(filedb.id), "original.pdf")
        self._ocr_path: Path = Path(BASE_FILE_DIR, str(filedb.id), "ocr.pdf")
        self.file: UploadFile = file
        self.db_file = filedb

    @classmethod
    def new(cls, user: User, file: UploadFile) -> Self:
        if not PDFFile.is_pdf_file(file):
            raise InvalidFileFormatException(file, "musst be a pdf!")

        db_file = FilesDB.new(user, file.filename)

        file = PDFFile(file, db_file)

        return file

    @classmethod
    def load(cls, user: User, file_id: UUID) -> Self:
        return PDFFile.load_with_db(FilesDB.get_with_text(user, file_id))

    @classmethod
    def load_with_db(cls, filedb: FilesDB) -> Self:
        raw_file = Path(BASE_FILE_DIR, str(filedb.id), "original.pdf").read_bytes()
        file = UploadFile(raw_file, filename=filedb.filename)

        return cls(file, filedb)

    @property
    def ocr_path(self) -> Path | None:
        if self._ocr_path.exists():
            return self._ocr_path

        return None

    @property
    def bytes(self) -> bytes:
        if len(self._bytes) == 0:
            self._bytes = self.path.read_bytes()

        return self._bytes

    @property
    def text(self) -> str:
        return self.path.read_text("utf-8")

    @staticmethod
    def is_pdf_file(file: UploadFile) -> bool:
        return file.filename.lower().endswith(".pdf")

    def save(self):
        if not self.path.exists():
            os.mkdir(self.path.parent)

        with self.path.open("wb") as fw:
            fw.write(self.file.file.read())

    def delete(self):
        os.remove(self.path)

    def ocr(self, force: bool = False):
        if force is False and self.ocr_path is not None:
            return self._ocr_path

        if self.original_has_ocr() and force is False:
            ocr_pdf(self.path, self._ocr_path, skip_text=True, force=False)
            return

        ocr_pdf(self.path, self._ocr_path, skip_text=False, force=True)

    def original_has_ocr(self) -> bool:
        file_text = extract_text_from_pdf(self.path)

        return file_text is not None or len(file_text) != 0

    def write_text_to_db(self, user: User):
        if self.ocr_path is None:
            raise InvalidFileOcrStatusException(self.file)

        text: list[str] = extract_text_from_pdf(self._ocr_path)

        ft: FileTextDB = FileTextDB.get_by_file_id(self.db_file.id, user)
        ft.save_file_text(text)
