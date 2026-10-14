import os
import pytest
from database import init_db
from auth import register_user
from medicine_service import add_medicine, log_dose
from pdf_service import generate_monthly_health_summary_pdf

import uuid

@pytest.fixture
def pdf_test_user():
    init_db()
    uid = uuid.uuid4().hex[:8]
    _, _, parent = register_user(f"parent_pdf_{uid}@example.com", "Password123!", "PDF Parent", "parent")
    _, _, stranger = register_user(f"stranger_pdf_{uid}@example.com", "Password123!", "Stranger", "child")
    return parent, stranger

def test_monthly_pdf_summary_generation(pdf_test_user):
    parent, stranger = pdf_test_user
    user_id = parent["id"]

    # Add medicine and dose log for October 2026
    med_id = add_medicine(user_id, "BP Medicine", "10mg", "Daily", ["morning"])
    log_dose(user_id, med_id, "morning", "2026-10-05", "taken", parent)

    # Generate summary
    pdf_path = generate_monthly_health_summary_pdf(user_id, "2026-10", parent)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000

    # Stranger should be blocked by authorization checks
    with pytest.raises(PermissionError):
        generate_monthly_health_summary_pdf(user_id, "2026-10", stranger)

    # Clean up generated PDF
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
