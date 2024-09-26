from pathlib import Path
from uuid import UUID
from pydantic import BaseModel, Field

from api.modules.language.languages import Languages


class FileUploadResponse(BaseModel):
    id: UUID
    path: Path


class FileUploadRequest(BaseModel):
    filename: str | None = Field(
        None, desription="Filename to overwrite the current one"
    )
    force_ocr: bool = Field(False, description="redo all ocr")
    skip_text: bool = Field(
        False, description="If set to False and OCR is detected donot overwrite it."
    )
    language: Languages | None = Field(
        None,
        title="file language",
        description="Set a language for this document. If None is given auto detect it",
    )
