import os
import sys
import time
from pathlib import Path
from typing import Self
from uuid import UUID
from fastapi import APIRouter, Depends, File as FastFile, UploadFile, BackgroundTasks
from pydantic import BaseModel, Field

from api.modules.language.languages import Languages
from api.routers.files.models import (
    FileOcrResponse,
    FileResponse,
    FileUploadRequest,
    FileUploadResponse,
)


sys.path.append(".")
from api.auth import validate_token
from api.db.models.users import User
from api.modules.file.pdffile import PDFFile, FilesDB
from api.exceptions.file import InvalidFileFormatException

router = APIRouter(prefix="/files", tags=["Files"])


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


@router.post(
    "/async_upload",
    response_model=FileUploadResponse,
    description="Upload the file, then process in the background",
)
async def async_upload_file(
    background_task: BackgroundTasks,
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

    background_task.add_task(
        ocr_file(file.db_file.id, file_upload_request.force_ocr, user)
    )

    return FileUploadResponse.from_pdffile(file)


@router.post("/ocr", response_model=FileOcrResponse)
async def ocr_file(
    id: UUID, force: bool = False, user: User = Depends(validate_token)
) -> FileOcrResponse:
    process_start = time.time()
    file = PDFFile.load(user, id)

    ocr_start = time.time()
    file.ocr(force)
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


# @router.put("/update")
# async def update_file_data(
#     id: UUID,
#     filename: None | str = None,
#     language: None | Languages = None,
#     user: User = Depends(validate_token)
# ):


@router.get("/detect_language", response_model=str)
async def detect_file_language(
    file_id: UUID, user: User = Depends(validate_token)
) -> str:
    return FilesDB.get_with_text(user, id).detect_language()


@router.post("/set_language", response_model=Languages)
async def set_file_language(
    file_id: UUID, language: Languages, user: User = Depends(validate_token)
) -> str:
    return language
