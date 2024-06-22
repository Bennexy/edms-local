import sys
from typing import Dict

from fastapi import UploadFile

sys.path.append(".")

from api.exceptions.base import ServerHTTPException


class InvalidFileFormatException(ServerHTTPException):
    def __init__(self, file: UploadFile, additional_message: str = None) -> None:

        self.filename = file.filename

        self.mesage = f"The File is not a pdf. {file.filename} - {additional_message}"

        status_code = 400
        super().__init__(status_code, detail = self.mesage)