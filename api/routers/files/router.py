import sys
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, File as FastFile, UploadFile
from pydantic import BaseModel

sys.path.append(".")
from api.auth import validate_token
from api.db.models.users import User
from api.modules.files.pdffile import PDFFile, FilesDB

router = APIRouter(prefix="/files")

from api.config import BASE_FILE_DIR  # noqa: E402


@router.get("/base_path")
async def get_base_path() -> str:
    return BASE_FILE_DIR.as_posix()


class UploadFileResponse(BaseModel):
    id: UUID
    path: Path


class FileUploadRequest(BaseModel):
    filename: str | None = None


@router.post("/upload")
async def upload_file(
    file_upload_request: FileUploadRequest,
    user: User = Depends(validate_token),
    file_data: UploadFile = FastFile(...),
) -> UploadFileResponse:
    file = PDFFile()

    file_id = FilesDB.new(user, file.filename)
    FilesDB
