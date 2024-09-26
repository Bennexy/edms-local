from enum import StrEnum


class Languages(StrEnum):
    DANISH = ("da", "danish")
    DUTCH = ("nl", "dutch")
    ENGLISH = ("en", "english")
    FINNISH = ("fi", "finnish")
    FRENCH = ("fr", "french")
    GERMAN = ("de", "german")
    HUNGARIAN = ("hu", "hungarian")
    ITALIAN = ("it", "italian")
    NORWEGIAN = ("no", "norwegian")
    PORTUGUESE = ("pt", "portuguese")
    ROMANIAN = ("ro", "romanian")
    RUSSIAN = ("ru", "russian")
    SPANISH = ("es", "spanish")
    SWEDISH = ("sv", "swedish")
    TURKISH = ("tr", "turkish")
    SIMPLE = ("simple", "simple")

    def __init__(self, language_code: str, language_name: str) -> None:
        super().__init__()
        self.language_name: str = language_name
        self.language_code: str = language_code

    def __new__(cls, language_code, language_name):
        obj = str.__new__(cls, language_code)
        obj._value_ = language_code
        obj.language_code = language_code
        obj.language_name = language_name
        return obj

    @classmethod
    def _missing_(cls, value):
        # This method is called when a value is not found in the enum
        for member in cls:
            if member.language_name == value or member.value == value:
                return member
        raise ValueError(f"No language found for value: {value}")

    def __eq__(self, other):
        if isinstance(other, Languages):
            return (
                self.value == other.value or self.language_name == other.language_name
            )
        elif isinstance(other, str):
            return self.value == other or self.language_name == other
        return NotImplemented

    def name(self) -> str:
        return self.language_name


if __name__ == "__main__":
    assert Languages.GERMAN == Languages("de")
    assert Languages.GERMAN == Languages("german")
    assert Languages.GERMAN == "de"
    assert Languages.GERMAN == "german"
