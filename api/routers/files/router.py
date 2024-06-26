import os
import sys
import time
from pathlib import Path
from typing import Self
from uuid import UUID
from fastapi import APIRouter, Depends, File as FastFile, UploadFile
from pydantic import BaseModel, Field


sys.path.append(".")
from api.auth import validate_token
from api.db.models.users import User
from api.modules.file.pdffile import PDFFile, FilesDB
from api.exceptions.file import InvalidFileFormatException

router = APIRouter(prefix="/files")

from api.config import BASE_FILE_DIR  # noqa: E402


@router.get("/base_path")
async def get_base_path() -> str:
    return BASE_FILE_DIR.as_posix()


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
    file_text: list[str]


class FileUploadRequest(BaseModel):
    filename: str | None = None


def get_file_size_mb(file_path) -> float:
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / 1024 / 1024
    return float("{:.2f}".format(size_mb))


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file_upload_request: FileUploadRequest = Depends(FileUploadRequest),
    file_data: UploadFile = FastFile(...),
    user: User = Depends(validate_token),
) -> FileUploadResponse:
    if not PDFFile.is_pdf_file(file_data):
        raise InvalidFileFormatException(file_data, "musst be a pdf!")

    if file_upload_request.filename is not None:
        if not file_upload_request.filename.lower().endswith(".pdf"):
            file_upload_request.filename += ".pdf"
        file_data.filename = file_upload_request.filename

    file = PDFFile.new(user, file_data)
    file.save()

    return FileUploadResponse.from_pdffile(file)


@router.post("/ocr", response_model=FileOcrResponse)
async def ocr_file(id: UUID, user: User = Depends(validate_token)) -> FileOcrResponse:
    process_start = time.time()
    file = PDFFile.load(user, id)

    ocr_start = time.time()
    file.ocr()
    full_text_start = time.time()
    file.write_text_to_db(user)
    process_end = time.time()

    return FileOcrResponse.from_pdffile(
        file,
        process_end - process_start,
        full_text_start - ocr_start,
        process_end - full_text_start,
    )


@router.get("/get", response_model=FileResponse)
async def get_file(id: UUID, user: User = Depends(validate_token)) -> FileResponse:
    file = PDFFile.load(user, id)

    return FileResponse(
        id=file.db_file.id,
        file_name=file.db_file.filename,
        file_text=file.db_file.file_text.file_text,
    )


@router.get("/list", response_model=list[FileResponse])
async def list_all(user: User = Depends(validate_token)) -> list[UUID]:
    files: list[FilesDB] = FilesDB.list_all(user)

    ret = list()
    for file in files:
        ret.append(
            FileResponse(
                id=file.id, file_name=file.filename, file_text=file.file_text.file_text
            )
        )

    return ret


@router.get("/full_text_search", response_model=list[UUID])
async def get_file_full_text_search(
    text: str, user: User = Depends(validate_token)
) -> list[UUID]:
    return FilesDB.find_by_text(user, text)
