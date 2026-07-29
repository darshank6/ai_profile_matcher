from docx import Document
from pypdf import PdfReader


def extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def extract_docx_text(file_path: str) -> str:
    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        if paragraph.text:
            text += paragraph.text + "\n"

    return text.strip()


def extract_txt_text(file_path: str) -> str:
    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:
        return file.read().strip()


def extract_text_from_file(
    file_path: str,
    file_extension: str
) -> str:
    if file_extension == ".pdf":
        return extract_pdf_text(file_path)

    if file_extension == ".docx":
        return extract_docx_text(file_path)

    if file_extension == ".txt":
        return extract_txt_text(file_path)

    return ""