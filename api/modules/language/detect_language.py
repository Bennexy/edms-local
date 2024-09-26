from typing import TypedDict
import warnings
from charset_normalizer import detect
from api.modules.language.languages import Languages


class Detected(TypedDict):
    language: str
    confidence: float
    encoding: str


def detect_language(text: bytes | str | list[str] | None) -> Languages:
    """
    defaults to Languages.ENGLISH
    """
    if text is None:
        return Languages.ENGLISH

    if isinstance(text, str):
        text = text.encode()
    elif isinstance(text, list):
        text = " ".join(text)
        if isinstance(text, str):
            text = text.encode()

    detected: Detected = detect(text)
    try:
        return Languages(detected["language"].lower())
    except ValueError:
        return Languages.ENGLISH
