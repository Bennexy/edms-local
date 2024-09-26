import sys

sys.path.append(".")

from api.modules.language.languages import Languages
from api.modules.language.detect_language import detect_language


def test_languages_eq_and_init():
    assert Languages.GERMAN == Languages("de")
    assert Languages.GERMAN == Languages("german")
    assert Languages.GERMAN == "de"
    assert Languages.GERMAN == "german"


def test_detect_languages_de():
    text = "Hallo, ich wünsche euch einen Schönen Tag!"
    assert Languages.GERMAN == detect_language(text)


def test_detect_languages_de_list():
    text = ["Hallo, ich wünsche euch einen Schönen Tag!", "123"]
    assert Languages.GERMAN == detect_language(text)


def test_detect_languages_en():
    text = "Howdy, i wisch yall a wonderfull day!"
    assert Languages.ENGLISH == detect_language(text)


def test_detect_languages_none():
    text = "34".encode()
    assert Languages.ENGLISH == detect_language(text)
