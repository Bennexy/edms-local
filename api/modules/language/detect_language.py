from typing import TypedDict
import warnings
from charset_normalizer import detect
from api.modules.language.languages import Languages


class Detected(TypedDict):
    language: str
    confidence: float
    encoding: str


def detect_language(text: bytes | str | list[str]) -> Languages:
    if isinstance(text, str):
        text = text.encode()
    elif isinstance(text, list):
        text = " ".join(text)
        if isinstance(text, str):
            text = text.encode()

    detected: Detected = detect(text)

    return Languages(detected["language"].lower())
