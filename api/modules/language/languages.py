from enum import StrEnum


class Languages(StrEnum):
    DANISH = ("danish", "da")
    DUTCH = ("dutch", "nl")
    ENGLISH = ("english", "en")
    FINNISH = ("finnish", "fi")
    FRENCH = ("french", "fr")
    GERMAN = ("german", "de")
    HUNGARIAN = ("hungarian", "hu")
    ITALIAN = ("italian", "it")
    NORWEGIAN = ("norwegian", "no")
    PORTUGUESE = ("portuguese", "pt")
    ROMANIAN = ("romanian", "ro")
    RUSSIAN = ("russian", "ru")
    SPANISH = ("spanish", "es")
    SWEDISH = ("swedish", "sv")
    TURKISH = ("turkish", "tr")
    SIMPLE = ("simple", "simple")

    def __init__(self, language_name: str, language_code: str) -> None:
        super().__init__()
        self.language_name: str = language_name
        self.language_code: str = language_code

    def __new__(cls, language_name, language_code):
        obj = str.__new__(cls, language_name)
        obj._value_ = language_name
        obj.language_code = language_code
        obj.language_name = language_name
        return obj

    @classmethod
    def _missing_(cls, value):
        # This method is called when a value is not found in the enum
        for member in cls:
            if member.language_code == value or member.value == value:
                return member
        raise ValueError(f"No language found for value: {value}")

    def __eq__(self, other):
        if isinstance(other, Languages):
            return (
                self.value == other.value or self.language_code == other.language_code
            )
        elif isinstance(other, str):
            return self.value == other or self.language_code == other
        return NotImplemented

    def code(self) -> str:
        return self.language_code


if __name__ == "__main__":
    assert Languages.GERMAN == Languages("de")
    assert Languages.GERMAN == Languages("german")
    assert Languages.GERMAN == "de"
    assert Languages.GERMAN == "german"
