import time
from fastapi import APIRouter, Depends, File as FastApiFile, UploadFile
from fastapi.responses import StreamingResponse

from api.auth import validate_token
from api.db.models.users import User
from api.exceptions.file import InvalidFileFormatException
from api.modules.file.file_processor import File, FileProcessor
from api.modules.file.pdffile import PDFFile


router = APIRouter(prefix="/ocr", tags=["OCR"])

FILE_RETURN_HEADERS = {
    "Content-Disposition": 'inline; filename="sample.pdf"',
    "content-type": "application/octet-stream",
}


@router.post("/ocr_file")
async def ocr(
    upload_file: UploadFile = FastApiFile(...),
    force: bool = False,
    user: User = Depends(validate_token),
) -> StreamingResponse:
    if not PDFFile.is_pdf_file(upload_file):
        raise InvalidFileFormatException(upload_file, "musst be a pdf!")

    file = File(upload_file)

    file_processor = FileProcessor(file)
    start = time.process_time()
    file_processor.ocr(force)
    durration = time.process_time() - start

    return StreamingResponse(
        open(file_processor.ocr_path, "rb"),
        media_type="application/pdf",
        headers={
            "processing-time-seconds": f"{durration:0.4}",
            "file-has-ocr": str(file_processor.file_has_text),
            "Content-Disposition": f'inline; filename="{file.upload_file.filename}"',
            "content-type": "application/octet-stream",
        },
    )
