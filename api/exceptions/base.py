import sys
sys.path.append(".")

from logger import get_logger
from fastapi import HTTPException
from typing import Any, Optional, Dict

logger = get_logger()

class ServerException(Exception):
    def __init__(self, message: str = None, exception: Exception = None, extended_information: dict = None, *args: object) -> None:
        self.message = message
        self.exception = exception
        self.extended_information = extended_information
        logger.exception(f'Exception {exception}')

        super().__init__(*args)

class ServerHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: Any = None, exception: Exception = None, headers: Optional[Dict[str, Any]] = None) -> None:
        logger.exception(f'Staus Code: {status_code} returned. Detail: {detail}, Exception {exception}')
        super().__init__(status_code, detail, headers)
    pass