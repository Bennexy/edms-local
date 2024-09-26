from pathlib import Path
from uuid import UUID
from pydantic import BaseModel, Field


from api.db.models.files import Files as FilesDB
from api.modules.language.languages import Languages


class FileUploadResponse(BaseModel):
    id: UUID
    path: Path


class FileResponse(BaseModel):
    id: UUID
    file_name: str
    file_text: list[str] | None = None

    @staticmethod
    def from_files(orm: FilesDB, with_text: bool) -> "FileResponse":
        file_text = None if orm.file_text is None else orm.file_text.file_text
        return FileResponse(
            id=orm.id,
            file_name=orm.filename,
            file_text=file_text if with_text else None,
        )


class FileUploadRequest(BaseModel):
    filename: str | None = Field(
        None, desription="Filename to overwrite the current one"
    )
    force_ocr: bool = Field(False, description="redo all ocr")
    skip_text: bool = Field(
        True, description="If set to False and OCR is detected donot overwrite it."
    )
    language: Languages | None = None
