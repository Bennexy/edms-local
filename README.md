ben
Test123$

## Dev setup
Python version: 3.12.3

I use pyenv to controll the python environment. 

Install project dependencies

You need to create a `.env` file that contains following values:
| *KEY* | *VALUE* |
| ----- | ------- |
| DATABASE_URI |  |


## Install Dependencies
`source venv/bin/activate && pip install -r requirements.txt`
[Tesseract](https://medium.com/@nothanjack/easy-installation-of-tesseract-ocr-on-debian-12-terminal-walkthrough-13120ec7d98c) - Used for OCR
[JBIG2](https://ocrmypdf.readthedocs.io/en/latest/jbig2.html) - used for image optimizations
[pngquant](https://pngquant.org/) - image optimizations ```sudo apt install pngquant```
[unpaper](https://github.com/unpaper/unpaper) - Clean image background ```sudo apt install unpaper```
[poppler-utils](https://poppler.freedesktop.org/) - Pillow pdf2image dependency ```sudo apt install poppler-utils```


## DB-Migration
Create alembic version: `./revision`
Apply revision: `alembic upgrade head`

## Improvements
- [ ] Set up dockerization
- [ ] Implement Language detection
- [ ] Implement multi language full text search (depends on language detection)
- [x] Implement pdf compression
- [ ] Implement conversion of other file types to pdf
- [ ] Clean up interfaces
- [ ] Oauth authentication




For language detection try this
```
from langdetect import detect
from sqlalchemy import create_engine, Column, Integer, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import TSVECTOR

Base = declarative_base()

class FileText(Base):
    __tablename__ = 'file_text'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer)
    file_text = Column(Text)
    _search_vector = Column(TSVECTOR, name='search_vector', nullable=False)

    @staticmethod
    def detect_language(text):
        try:
            return detect(text)
        except:
            return 'english'  # Default to English if detection fails

    @staticmethod
    def get_tsvector_language(language_code):
        if language_code == 'de':
            return 'german'
        elif language_code == 'en':
            return 'english'
        else:
            return 'english'  # Default to English

    def update_search_vector(self):
        language_code = self.detect_language(self.file_text)
        tsvector_language = self.get_tsvector_language(language_code)
        self._search_vector = func.to_tsvector(tsvector_language, self.file_text)

```