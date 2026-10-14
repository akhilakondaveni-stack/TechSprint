import pytest
from datetime import date
from database import init_db
from auth import register_user
from medicine_service import (
    add_medicine,
    update_medicine,
    delete_medicine,
    get_user_medicines,
    log_dose,
    get_daily_schedule_with_logs,
    get_adherence_stats,
    MISSED_DOSE_SAFETY_RULE
)

import uuid

@pytest.fixture
def test_parent():
    init_db()
    email = f"parent_med_{uuid.uuid4().hex[:8]}@example.com"
    _, _, user = register_user(email, "Password123!", "Med Test Parent", "parent")
    return user

def test_add_and_get_medicines(test_parent):
    user_id = test_parent["id"]
    med_id = add_medicine(
        user_id=user_id,
        name="Amlodipine",
        dose="5 mg",
        frequency="Once daily",
        timing_slots=["morning"],
        food_instruction="After Food"
    )
    assert med_id > 0

    meds = get_user_medicines(user_id, test_parent)
    assert len(meds) >= 1
    found = [m for m in meds if m["id"] == med_id][0]
    assert found["name"] == "Amlodipine"
    assert found["timing_slots"] == ["morning"]

def test_duplicate_dose_prevention_and_correction(test_parent):
    user_id = test_parent["id"]
    med_id = add_medicine(
        user_id=user_id,
        name="Metformin",
        dose="500 mg",
        frequency="Once daily",
        timing_slots=["morning"]
    )

    today_str = date.today().isoformat()

    # Log initial dose as 'taken'
    ok1 = log_dose(user_id, med_id, "morning", today_str, "taken", test_parent, notes="Initial entry")
    assert ok1 is True

    # Check schedule
    sched = get_daily_schedule_with_logs(user_id, today_str, test_parent)
    item = [x for x in sched if x["medicine_id"] == med_id][0]
    assert item["status"] == "taken"

    # User accidentally clicked taken, corrects it to 'skipped' on same date and slot
    # Must NOT create a duplicate record, must update the existing record!
    ok2 = log_dose(user_id, med_id, "morning", today_str, "skipped", test_parent, notes="Corrected accidentally marked")
    assert ok2 is True

    sched_after = get_daily_schedule_with_logs(user_id, today_str, test_parent)
    items_after = [x for x in sched_after if x["medicine_id"] == med_id]
    assert len(items_after) == 1  # exactly one record!
    assert items_after[0]["status"] == "skipped"

def test_adherence_calculation(test_parent):
    user_id = test_parent["id"]
    med_id = add_medicine(user_id=user_id, name="Test Med", dose="10mg", frequency="Daily", timing_slots=["morning"])
    today_str = date.today().isoformat()

    log_dose(user_id, med_id, "morning", today_str, "taken", test_parent)
    stats = get_adherence_stats(user_id, days=7, current_user=test_parent)
    assert stats["taken"] >= 1
    assert stats["adherence_rate"] > 0

def test_missed_dose_safety_rule():
    assert "NEVER take a double dose" in MISSED_DOSE_SAFETY_RULE
