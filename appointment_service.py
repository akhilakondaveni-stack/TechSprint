import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple

from database import execute_query, execute_one, execute_insert, execute_update, log_audit
from auth import check_parent_access

logger = logging.getLogger(__name__)

def add_appointment(
    user_id: int,
    doctor_name: str,
    facility: str,
    appointment_date: str,
    appointment_time: str,
    contact_number: Optional[str],
    mode: str,
    notes: Optional[str],
    current_user: Dict[str, Any]
) -> int:
    """Creates a new medical appointment schedule."""
    if not check_parent_access(current_user, user_id):
        raise PermissionError("Unauthorized to schedule appointment for this user.")

    app_id = execute_insert("""
        INSERT INTO appointments (
            user_id, doctor_name, facility, appointment_date,
            appointment_time, contact_number, mode, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'upcoming', ?)
    """, (
        user_id,
        doctor_name.strip(),
        facility.strip(),
        appointment_date,
        appointment_time,
        contact_number.strip() if contact_number else None,
        mode,
        notes.strip() if notes else None
    ))

    log_audit(
        actor_id=current_user["id"],
        target_id=user_id,
        action="APPOINTMENT_ADDED",
        resource_type="appointments",
        resource_id=str(app_id)
    )
    return app_id

def update_appointment(
    app_id: int,
    doctor_name: str,
    facility: str,
    appointment_date: str,
    appointment_time: str,
    contact_number: Optional[str],
    mode: str,
    status: str,
    notes: Optional[str],
    current_user: Dict[str, Any]
) -> bool:
    """Updates an existing appointment."""
    app = execute_one("SELECT user_id FROM appointments WHERE id = ?", (app_id,))
    if not app:
        return False

    if not check_parent_access(current_user, app["user_id"]):
        raise PermissionError("Unauthorized to update this appointment.")

    count = execute_update("""
        UPDATE appointments
        SET doctor_name = ?, facility = ?, appointment_date = ?,
            appointment_time = ?, contact_number = ?, mode = ?,
            status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        doctor_name.strip(),
        facility.strip(),
        appointment_date,
        appointment_time,
        contact_number.strip() if contact_number else None,
        mode,
        status,
        notes.strip() if notes else None,
        app_id
    ))

    if count > 0:
        log_audit(
            actor_id=current_user["id"],
            target_id=app["user_id"],
            action="APPOINTMENT_UPDATED",
            resource_type="appointments",
            resource_id=str(app_id)
        )
        return True
    return False

def cancel_appointment(app_id: int, current_user: Dict[str, Any]) -> bool:
    """Marks an appointment as cancelled."""
    return update_appointment_status(app_id, "cancelled", current_user)

def update_appointment_status(app_id: int, new_status: str, current_user: Dict[str, Any]) -> bool:
    """Updates status to upcoming, completed, or cancelled."""
    if new_status not in ("upcoming", "completed", "cancelled"):
        return False

    app = execute_one("SELECT user_id FROM appointments WHERE id = ?", (app_id,))
    if not app:
        return False

    if not check_parent_access(current_user, app["user_id"]):
        raise PermissionError("Unauthorized appointment status change.")

    count = execute_update("""
        UPDATE appointments
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_status, app_id))

    if count > 0:
        log_audit(
            actor_id=current_user["id"],
            target_id=app["user_id"],
            action=f"APPOINTMENT_{new_status.upper()}",
            resource_type="appointments",
            resource_id=str(app_id)
        )
        return True
    return False

def get_user_appointments(
    user_id: int,
    current_user: Dict[str, Any],
    status_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves appointments sorted chronologically."""
    if not check_parent_access(current_user, user_id):
        raise PermissionError("Unauthorized access to appointments.")

    sql = """
        SELECT id, user_id, doctor_name, facility, appointment_date,
               appointment_time, contact_number, mode, status, notes, created_at
        FROM appointments
        WHERE user_id = ?
    """
    params = [user_id]
    if status_filter:
        sql += " AND status = ?"
        params.append(status_filter)

    sql += " ORDER BY appointment_date ASC, appointment_time ASC"
    rows = execute_query(sql, tuple(params))
    return [dict(r) for r in rows]
