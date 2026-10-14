import os
import io
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import pymupdf  # PyMuPDF
from PIL import Image

from config import MAX_PDF_PAGES
from security import (
    validate_uploaded_file,
    save_uploaded_file_securely,
    encrypt_text,
    decrypt_text,
)
from database import execute_query, execute_one, execute_insert, execute_update, log_audit
from auth import check_parent_access
from ai_service import analyze_medical_document, ReportExplanation

logger = logging.getLogger(__name__)

def process_uploaded_document_to_images(file_name: str, file_bytes: bytes) -> Tuple[bool, str, List[bytes]]:
    """
    Validates the uploaded file and converts PDF pages to list of PNG image bytes.
    If already an image (PNG/JPG), returns single image bytes.
    Enforces page limit (MAX_PDF_PAGES).
    """
    valid, err_msg = validate_uploaded_file(file_name, file_bytes)
    if not valid:
        return False, err_msg, []

    _, ext = os.path.splitext(file_name.lower())
    images_list = []

    try:
        if ext == ".pdf":
            # Process with PyMuPDF
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)
            if total_pages > MAX_PDF_PAGES:
                doc.close()
                return False, f"PDF exceeds maximum page limit of {MAX_PDF_PAGES} pages (document has {total_pages} pages).", []
            
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                images_list.append(img_bytes)
            doc.close()
        else:
            # Process image directly and ensure PIL can open it
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()
            images_list.append(file_bytes)

        return True, "", images_list
    except Exception as e:
        logger.error(f"Error processing document to images: {e}")
        return False, f"Could not process document pages: {str(e)}", []

def save_medical_report(
    user_id: int,
    title: str,
    report_date: str,
    doctor_name: Optional[str],
    facility_name: Optional[str],
    report_type: str,
    file_path: str,
    file_hash: str,
    extracted_data: Dict[str, Any],
    explanation: Dict[str, Any],
    actor_id: Optional[int] = None
) -> int:
    """
    Encrypts extracted sensitive medical data and saves the report to database.
    """
    extracted_json = json.dumps(extracted_data, ensure_ascii=False)
    explanation_json = json.dumps(explanation, ensure_ascii=False)

    encrypted_data = encrypt_text(extracted_json)
    encrypted_explanation = encrypt_text(explanation_json)

    report_id = execute_insert("""
        INSERT INTO medical_reports (
            user_id, title, report_date, doctor_name, facility_name,
            report_type, file_path, file_hash,
            extracted_data_encrypted, explanation_encrypted
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        title.strip() if title else "Medical Report",
        report_date,
        doctor_name.strip() if doctor_name else "",
        facility_name.strip() if facility_name else "",
        report_type,
        file_path,
        file_hash,
        encrypted_data,
        encrypted_explanation
    ))

    log_audit(
        actor_id=actor_id or user_id,
        target_id=user_id,
        action="REPORT_SAVED",
        resource_type="medical_reports",
        resource_id=str(report_id)
    )

    return report_id

def get_user_reports(user_id: int, current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retrieves all medical reports for a target user with authorization verification.
    """
    if not check_parent_access(current_user, user_id):
        raise PermissionError("Unauthorized access to user medical reports.")

    rows = execute_query("""
        SELECT id, user_id, title, report_date, doctor_name, facility_name,
               report_type, file_path, created_at
        FROM medical_reports
        WHERE user_id = ?
        ORDER BY report_date DESC, created_at DESC
    """, (user_id,))

    return [dict(r) for r in rows]

def get_report_details(report_id: int, current_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Retrieves and decrypts a specific medical report with authorization enforcement.
    """
    row = execute_one("""
        SELECT id, user_id, title, report_date, doctor_name, facility_name,
               report_type, file_path, file_hash,
               extracted_data_encrypted, explanation_encrypted, created_at
        FROM medical_reports
        WHERE id = ?
    """, (report_id,))

    if not row:
        return None

    report = dict(row)
    if not check_parent_access(current_user, report["user_id"]):
        log_audit(
            actor_id=current_user["id"],
            target_id=report["user_id"],
            action="UNAUTHORIZED_REPORT_ACCESS_ATTEMPT",
            resource_type="medical_reports",
            resource_id=str(report_id)
        )
        raise PermissionError("Unauthorized access to this medical report.")

    # Decrypt sensitive data
    decrypted_data_str = decrypt_text(report["extracted_data_encrypted"])
    decrypted_expl_str = decrypt_text(report["explanation_encrypted"])

    try:
        report["extracted_data"] = json.loads(decrypted_data_str) if decrypted_data_str else {}
    except Exception:
        report["extracted_data"] = {}

    try:
        report["explanation"] = json.loads(decrypted_expl_str) if decrypted_expl_str else {}
    except Exception:
        report["explanation"] = {}

    log_audit(
        actor_id=current_user["id"],
        target_id=report["user_id"],
        action="REPORT_VIEWED",
        resource_type="medical_reports",
        resource_id=str(report_id)
    )

    return report

def delete_medical_report(report_id: int, current_user: Dict[str, Any]) -> bool:
    """
    Deletes a medical report if the user owns it or has approved family authorization.
    """
    report = execute_one("SELECT id, user_id, file_path FROM medical_reports WHERE id = ?", (report_id,))
    if not report:
        return False

    if not check_parent_access(current_user, report["user_id"]):
        raise PermissionError("Unauthorized deletion attempt.")

    # Remove physical file if exists
    try:
        if os.path.exists(report["file_path"]):
            os.remove(report["file_path"])
    except Exception as e:
        logger.warning(f"Could not remove physical report file: {e}")

    count = execute_update("DELETE FROM medical_reports WHERE id = ?", (report_id,))
    if count > 0:
        log_audit(
            actor_id=current_user["id"],
            target_id=report["user_id"],
            action="REPORT_DELETED",
            resource_type="medical_reports",
            resource_id=str(report_id)
        )
        return True
    return False
