import sys
from pathlib import Path
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field

from api.db.models.files import Files
from api.modules.language.languages import Languages


sys.path.append(".")

from api.modules.file.pdffile import PDFFile
from api.routers.process.helper import get_file_size_mb


class FileUploadResponse(BaseModel):
    id: UUID
    path: Path

    @staticmethod
    def from_pdffile(pdffile: PDFFile) -> Self:
        return FileUploadResponse(id=pdffile.db_file.id, path=pdffile.path)


class FileOcrResponse(BaseModel):
    id: UUID
    success: bool = True
    message: str = None
    ocr_path: Path
    process_time: float = Field(description="Proccessing time in seconds")
    ocr_time: float = Field(description="Time in seconds spent at ocring the pdf")
    full_text_search_creation_time: float = Field(
        description="Time in seconds spend at reading and saveing the text from the ocred pdf"
    )

    file_size: float
    ocr_file_size: float

    @staticmethod
    def from_pdffile(
        pdffile: PDFFile,
        process_time: float,
        ocr_time: float,
        full_text_search_creation_time: float,
    ) -> Self:
        return FileOcrResponse(
            id=pdffile.db_file.id,
            ocr_path=pdffile.ocr_path,
            process_time=process_time,
            ocr_time=ocr_time,
            full_text_search_creation_time=full_text_search_creation_time,
            file_size=get_file_size_mb(pdffile.path),
            ocr_file_size=get_file_size_mb(pdffile.ocr_path),
        )


class FileResponse(BaseModel):
    id: UUID
    file_name: str

    def from_files(cls, orm: Files) -> "FileResponse":
        obj: FileResponse = cls()
        obj.id = orm.id
        obj.file_name = orm.filename


class FileTextResponse(FileResponse):
    file_language: Languages
    file_text: list[str]

    @classmethod
    def from_files(cls, orm: Files) -> "FileTextResponse":
        obj: FileTextResponse = cls()

        obj.id = orm.id
        obj.file_name = orm.filename
        obj.file_language = orm.file_text.file_language
        obj.file_text = orm.file_text.file_text


class FileUploadRequest(BaseModel):
    filename: str | None = None
    force_ocr: bool = Field(
        False, description="If set to False and OCR is detected donot overwrite it."
    )
    language: Languages | None = Field(
        None,
        description="Set a language for this document. If None is given auto detect it",
    )
