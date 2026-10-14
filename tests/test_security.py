import os
import pytest
from security import (
    encrypt_text,
    decrypt_text,
    validate_uploaded_file,
    save_uploaded_file_securely,
    is_rate_limited
)

def test_fernet_encryption_and_decryption():
    secret_text = "Fasting Blood Glucose: 110 mg/dL, HbA1c: 6.2%"
    encrypted = encrypt_text(secret_text)
    assert encrypted != secret_text
    assert len(encrypted) > len(secret_text)

    decrypted = decrypt_text(encrypted)
    assert decrypted == secret_text

def test_invalid_ciphertext_handling():
    garbage = "this_is_not_a_valid_fernet_token"
    res = decrypt_text(garbage)
    assert "Decryption Error" in res

def test_file_upload_validation_valid():
    # Valid PDF magic header
    pdf_bytes = b"%PDF-1.4\n%test pdf content"
    valid, msg = validate_uploaded_file("report.pdf", pdf_bytes)
    assert valid is True
    assert msg == ""

    # Valid PNG magic header
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    valid, msg = validate_uploaded_file("scan.png", png_bytes)
    assert valid is True

    # Valid JPG magic header
    jpg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    valid, msg = validate_uploaded_file("lab.jpg", jpg_bytes)
    assert valid is True

def test_file_upload_validation_malformed_and_mime_spoofing():
    # File named .pdf but containing arbitrary text (spoofed header)
    fake_pdf = b"Hello I am just plaintext pretending to be a PDF"
    valid, msg = validate_uploaded_file("sneaky.pdf", fake_pdf)
    assert valid is False
    assert "File content header does not match" in msg

    # Disallowed extension
    exe_bytes = b"MZ\x90\x00\x03\x00\x00\x00"
    valid, msg = validate_uploaded_file("malware.exe", exe_bytes)
    assert valid is False
    assert "Unsupported file type" in msg

def test_oversized_file_rejection():
    # 11MB file exceeds 10MB limit
    huge_bytes = b"%PDF" + (b"0" * (11 * 1024 * 1024))
    valid, msg = validate_uploaded_file("huge.pdf", huge_bytes)
    assert valid is False
    assert "exceeds maximum allowed size" in msg

def test_safe_file_saving_prevents_path_traversal():
    pdf_bytes = b"%PDF-1.5 test document"
    # Attempt path traversal in original name
    traversal_name = "../../../etc/passwd.pdf"
    saved_path, file_hash = save_uploaded_file_securely(traversal_name, pdf_bytes)

    assert os.path.exists(saved_path)
    assert ".." not in saved_path
    assert saved_path.endswith(".pdf")
    assert len(file_hash) == 64  # valid SHA-256

    # Cleanup
    if os.path.exists(saved_path):
        os.remove(saved_path)
