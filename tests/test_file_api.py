import io

import fitz
import pytest
from docx import Document
from PIL import Image, ImageDraw, ImageFont

from app import create_app

@pytest.fixture
def client():

    app = create_app()

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_txt_file_upload(client):

    file_content = "తిన్నావా?"

    response = client.post(
        "/api/v1/transliterate/file",
        data={
            "file": (
                io.BytesIO(file_content.encode("utf-8")),
                "telugu.txt"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["filename"] == "telugu.txt"
    assert data["data"]["original_text"] == "తిన్నావా?"
    assert data["data"]["language"] == "telugu"
    assert data["data"]["transliterated_text"] == "tinnava?"


def test_pdf_file_upload(client):

    pdf = fitz.open()

    page = pdf.new_page()

    page.insert_text(
        (72, 72),
        "Hello world"
    )

    pdf_bytes = pdf.tobytes()

    pdf.close()

    response = client.post(
        "/api/v1/transliterate/file",
        data={
            "file": (
                io.BytesIO(pdf_bytes),
                "english.pdf"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["filename"] == "english.pdf"
    assert "Hello world" in data["data"]["original_text"]
    assert data["data"]["language"] == "english"
    assert data["data"]["transliterated_text"] == "Hello world"


def test_telugu_pdf_file_upload(client):

    pdf = fitz.open()

    page = pdf.new_page()

    font = fitz.Font(
        fontfile=r"C:\Windows\Fonts\Nirmala.ttc"
    )

    page.insert_text(
        (72, 72),
        "తిన్నావా?",
        fontname="NirmalaUI",
        fontfile=r"C:\Windows\Fonts\Nirmala.ttc",
        fontsize=18
    )

    pdf_bytes = pdf.tobytes()

    pdf.close()

    response = client.post(
        "/api/v1/transliterate/file",
        data={
            "file": (
                io.BytesIO(pdf_bytes),
                "telugu.pdf"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["filename"] == "telugu.pdf"
    assert "తిన్నావా?" in data["data"]["original_text"]
    assert data["data"]["language"] == "telugu"
    assert data["data"]["transliterated_text"] == "tinnava?"
    
    
def test_telugu_docx_file_upload(client):

    document = Document()

    document.add_paragraph(
        "తిన్నావా?"
    )

    docx_bytes = io.BytesIO()

    document.save(docx_bytes)

    docx_bytes.seek(0)

    response = client.post(
        "/api/v1/transliterate/file",
        data={
            "file": (
                docx_bytes,
                "telugu.docx"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["filename"] == "telugu.docx"
    assert "తిన్నావా?" in data["data"]["original_text"]
    assert data["data"]["language"] == "telugu"
    assert data["data"]["transliterated_text"] == "tinnava?"
    
    
def test_english_image_file_upload(client):

    image = Image.new(
        "RGB",
        (1000, 300),
        "white"
    )

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        r"C:\Windows\Fonts\arial.ttf",
        72
    )

    draw.text(
        (100, 90),
        "Hello world",
        font=font,
        fill="black"
    )

    image_bytes = io.BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    response = client.post(
        "/api/v1/transliterate/file",
        data={
            "file": (
                image_bytes,
                "english.png"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["filename"] == "english.png"

    extracted_text = data["data"]["original_text"]

    assert "Hello" in extracted_text
    assert "world" in extracted_text

    assert data["data"]["language"] == "english"

    assert "Hello" in data["data"]["transliterated_text"]
    assert "world" in data["data"]["transliterated_text"]
    
    
def test_telugu_image_file_upload(client):

    image = Image.new(
        "RGB",
        (1200, 300),
        "white"
    )

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        r"C:\Windows\Fonts\Nirmala.ttc",
        72
    )

    draw.text(
        (100, 90),
        "తిన్నావా?",
        font=font,
        fill="black"
    )

    image_bytes = io.BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    response = client.post(
        "/api/v1/transliterate/file",
        data={
            "file": (
                image_bytes,
                "telugu.png"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["filename"] == "telugu.png"

    extracted_text = data["data"]["original_text"]

    assert "తిన్నావా?" in extracted_text

    assert data["data"]["language"] == "telugu"
    assert data["data"]["transliterated_text"] == "tinnava?"
    

def test_unsupported_file_extension(client):

    response = client.post(
        "/api/v1/transliterate/file",
        data={
            "file": (
                io.BytesIO(b"some test content"),
                "test.zip"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert "unsupported file type" in data["message"].lower()
    
def test_invalid_pdf_content(client):

    fake_pdf = b"This is not a real PDF file"

    response = client.post(
        "/api/v1/transliterate/file",
        data={
            "file": (
                io.BytesIO(fake_pdf),
                "fake.pdf"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert "invalid pdf file content" in data["message"].lower()
                                   