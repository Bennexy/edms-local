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

    def __new__(cls, language_name, language_code):
        obj = str.__new__(cls, language_name)
        obj._value_ = language_name
        obj.language_code = language_code
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


if __name__ == "__main__":
    assert Languages("german") == Languages("de")
    assert Languages("german") == Languages.GERMAN
