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
[ghostscript](https://ghostscript.readthedocs.io/en/latest/Install.html) - OCRmyPDF dependency

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


