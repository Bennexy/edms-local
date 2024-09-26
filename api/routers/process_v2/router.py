import os
import sys
import time
from pathlib import Path
from typing import Self
from uuid import UUID
from fastapi import APIRouter, Depends, File as FastApiFile, UploadFile, BackgroundTasks
from pydantic import BaseModel, Field

from api.db.models.files import FileText
from api.modules.language.languages import Languages
from api.routers.process_v2.models import (
    FileResponse,
    FileUploadRequest,
    FileUploadResponse,
)


sys.path.append(".")
from api.auth import validate_token
from api.db.models.users import User
from api.modules.file.file_processor import File, FileProcessor
from api.modules.file.pdffile import PDFFile, FilesDB
from api.exceptions.file import InvalidFileFormatException

router = APIRouter(prefix="/v2/process", tags=["Process V2"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file_upload_request: FileUploadRequest = Depends(),
    file: File = Depends(File.get_file),
    user: User = Depends(validate_token),
) -> FileUploadResponse:
    if not await file.is_pdf():
        raise InvalidFileFormatException(file, "musst be a pdf!")

    file.update_filename(file_upload_request.filename)

    db_file = FilesDB.new(user, file.filename, file.id)

    file_processor = FileProcessor(file)
    file_processor.ocr(file_upload_request.force_ocr, file_upload_request.skip_text)

    db_file.file_text.update_file_text(file_processor.file_text)

    return FileUploadResponse(id=file.id, path=file_processor.path)


@router.get("/get", response_model=FileResponse)
async def get_file(
    id: UUID, with_text: bool = False, user: User = Depends(validate_token)
) -> FileResponse:
    file: FilesDB = FilesDB.get_with_text(user, id)

    return FileResponse.from_files(file, with_text)


@router.get("/get_all", response_model=list[FileResponse])
async def get_all(
    with_text: bool = False, user: User = Depends(validate_token)
) -> list[UUID]:
    files: list[FilesDB] = FilesDB.list_all_with_text(user)

    ret = list()
    for file in files:
        ret.append(FileResponse.from_files(file, with_text=with_text))

    return ret


@router.get("/full_text_search", response_model=list[UUID])
async def get_file_full_text_search(
    text: str, user: User = Depends(validate_token)
) -> list[UUID]:
    return FilesDB.find_by_text(user, text)
