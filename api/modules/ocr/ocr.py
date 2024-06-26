from pathlib import Path

# import subprocess
# import tempfile
# import os
import ocrmypdf
import fitz


def ocr_pdf(input_pdf: Path, output_pdf: Path, skip_text: bool, force=False) -> None:
    # Run ocrmypdf to perform OCR
    ocrmypdf.ocr(
        input_pdf,
        output_pdf,
        language=["deu", "eng"],
        use_threads=True,
        force_ocr=force,
        jbig2_lossy=False,
        jbig2_threshold=0.85,  # if two symbols are 85% similar, they will be compressed together.
        optimize=3,
        clean=True,
        clean_final=True,
        # remove_background=True,  # NotImplementedError: --remove-background is temporarily not implemented
        output_type="pdf",
        rotate_pages=True,
        skip_text=skip_text,
    )


def extract_text_from_pdf(pdf_path: Path) -> list[str]:
    # Use PyMuPDF to extract text from each page of the PDF
    pdf_document = fitz.open(pdf_path)
    text_pages = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text()
        text_pages.append(page_text)

    return text_pages
