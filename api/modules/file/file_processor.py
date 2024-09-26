import os
from pathlib import Path
import shutil
import uuid
from fastapi import UploadFile
from fastapi import File as FastApiFile
from api.config import BASE_FILE_DIR
from api.modules.ocr import ocr
from logger.logger import get_logger


logger = get_logger()


class File(UploadFile):
    def __init__(self, ufile: UploadFile, *args, id: uuid.UUID | None = None, **kwargs):
        super().__init__(
            file=ufile.file,
            size=ufile.size,
            filename=ufile.filename,
            headers=ufile.headers,
        )

        self.id = id if id is not None else uuid.uuid4()

    def update_filename(self, filename: str | None) -> None:
        if filename is None:
            return

        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
            self.filename = filename

    async def is_pdf(self) -> bool:
        header_bytes = await self.read(5)
        await self.seek(0)
        return header_bytes == b"%PDF-"

    @staticmethod
    async def get_file(file: UploadFile = FastApiFile(...)) -> "File":
        return File(ufile=file)


class FileProcessor:
    def __init__(self, file: File, delete_file: bool = False) -> None:
        self.file: File = file
        self.delete_file: bool = delete_file

        self.folder_path: Path = Path(BASE_FILE_DIR, str(self.file.id))

        self.path: Path = Path(self.folder_path, "original.pdf")
        self.ocr_path: Path = Path(self.folder_path, "ocr.pdf")

        os.mkdir(self.folder_path)
        with self.path.open("wb") as fw:
            fw.write(self.file.file.read())

        self.__set_file_text()

    def __del__(self):
        if self.delete_file:
            shutil.rmtree(self.folder_path.absolute())

    def __set_file_text(self):
        self.file_text = ocr.extract_text_from_pdf(
            self.ocr_path if self.ocr_path.is_file() else self.path
        )

    def has_text(self) -> bool:
        return self.file_text is not None or len(self.file_text) != 0

    def ocr(self, force: bool = False, skip_text: bool = True) -> None:
        logger.info("ocring document")
        ocr.ocr_pdf(self.path, self.ocr_path, skip_text=skip_text, force=force)
        self.__set_file_text()
