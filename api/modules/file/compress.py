from io import BytesIO
from pathlib import Path
import tempfile
from pdf2image import convert_from_path
import os
from pypdf import PdfWriter, PageObject
import fitz
from PIL import Image


def compress_pdf(input_path: Path, output_path: Path):
    """
    removes all ocr data
    """
    images: list[Image.Image] = convert_from_path(
        input_path, thread_count=1, fmt="jpeg", jpegopt={"optimize": "progressive"}
    )

    images[0].save(
        output_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
    )


# def generate_thumbnail(input_path: Path, output_path: Path):
#     images: list[Image.Image] = convert_from_path(input_path, first_page=0, last_page=0, fmt=)


def compress_pdf_fitz(input_path, output_path, zoom_x=1.0, zoom_y=1.0, rotation=0):
    # Open the input PDF
    input_pdf: fitz.Document = fitz.open(input_path)
    input_pdf.save(output_path, garbage=4, deflate=True)

    input_pdf.close()

    # # Create a new PDF for the compressed output
    # output_pdf: fitz.Document = fitz.open()

    # # Iterate through each page
    # for page_num in range(len(input_pdf)):
    #     # Get the current page
    #     page: fitz.Page = input_pdf.load_page(page_num)

    #     # Define a transformation matrix for compression
    #     mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation)

    #     # Get the pixmap (image) of the page
    #     pix = page.get_pixmap(matrix=mat, alpha=False)

    #     # Create a new page in the output PDF with the compressed pixmap
    #     output_page: fitz.Page = output_pdf.new_page(width=pix.width, height=pix.height)
    #     output_page.insert_image(pix)

    # # Save the compressed PDF
    # output_pdf.save(output_path)
    # output_pdf.close()
    # input_pdf.close()


def get_file_size_mb(file_path) -> float:
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / 1024 / 1024
    return float("{:.2f}".format(size_mb))


if __name__ == "__main__":
    input_path = Path(
        "/home/ben/dev/edms-local/files/c972a285-9518-496d-8f24-69195785ebe2/original.pdf"
    )
    output_path = Path(
        "/home/ben/dev/edms-local/files/c972a285-9518-496d-8f24-69195785ebe2/compress_output.pdf"
    )

    compress_pdf(input_path, output_path)

    print(f"original: {get_file_size_mb(input_path)} MB")
    print(f"compressed: {get_file_size_mb(output_path)} MB")
