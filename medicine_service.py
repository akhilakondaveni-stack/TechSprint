import json
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional, Tuple

from database import execute_query, execute_one, execute_insert, execute_update, log_audit
from auth import check_parent_access

logger = logging.getLogger(__name__)

MISSED_DOSE_SAFETY_RULE = (
    "⚠️ MEDICAL SAFETY RULE: If you miss a dose, take it as soon as you remember unless it is almost "
    "time for your next scheduled dose. NEVER take a double dose or extra medication to make up for a missed dose."
)

MISSED_DOSE_SAFETY_RULE_HI = (
    "⚠️ सुरक्षा नियम: यदि कोई खुराक छूट जाती है, तो याद आने पर लें, जब तक कि अगली खुराक का समय न हो। "
    "छूटी हुई खुराक की भरपाई के लिए कभी भी दोहरी (डबल) खुराक न लें।"
)

MISSED_DOSE_SAFETY_RULE_TE = (
    "⚠️ భద్రతా నియమం: ఒకవేళ మందుల మోతాదు మిస్ అయితే, తదుపరి సమయం దగ్గరపడే వరకు గుర్తు రాగానే వేసుకోండి. "
    "కానీ ఎట్టి పరిస్థితుల్లోనూ ఒకేసారి డబుల్ డోస్ తీసుకోకూడదు."
)

def add_medicine(
    user_id: int,
    name: str,
    dose: str,
    frequency: str,
    timing_slots: List[str],
    food_instruction: str = "After Food",
    duration: Optional[str] = None,
    actor_id: Optional[int] = None
) -> int:
    """Adds a new active medicine schedule for a parent."""
    slots_json = json.dumps([s.lower() for s in timing_slots])
    
    med_id = execute_insert("""
        INSERT INTO medicines (user_id, name, dose, frequency, timing_slots, food_instruction, duration, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        user_id,
        name.strip(),
        dose.strip(),
        frequency.strip(),
        slots_json,
        food_instruction,
        duration.strip() if duration else ""
    ))
    
    log_audit(
        actor_id=actor_id or user_id,
        target_id=user_id,
        action="MEDICINE_ADDED",
        resource_type="medicines",
        resource_id=str(med_id)
    )
    return med_id

def update_medicine(
    med_id: int,
    name: str,
    dose: str,
    frequency: str,
    timing_slots: List[str],
    food_instruction: str,
    duration: Optional[str],
    is_active: bool,
    current_user: Dict[str, Any]
) -> bool:
    """Updates an existing medicine schedule with authorization validation."""
    med = execute_one("SELECT user_id FROM medicines WHERE id = ?", (med_id,))
    if not med:
        return False
    
    if not check_parent_access(current_user, med["user_id"]):
        raise PermissionError("Unauthorized update of medicine schedule.")
        
    slots_json = json.dumps([s.lower() for s in timing_slots])
    count = execute_update("""
        UPDATE medicines
        SET name = ?, dose = ?, frequency = ?, timing_slots = ?,
            food_instruction = ?, duration = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        name.strip(),
        dose.strip(),
        frequency.strip(),
        slots_json,
        food_instruction,
        duration.strip() if duration else "",
        1 if is_active else 0,
        med_id
    ))
    
    if count > 0:
        log_audit(
            actor_id=current_user["id"],
            target_id=med["user_id"],
            action="MEDICINE_UPDATED",
            resource_type="medicines",
            resource_id=str(med_id)
        )
        return True
    return False

def delete_medicine(med_id: int, current_user: Dict[str, Any]) -> bool:
    """Deletes a medicine schedule with authorization validation."""
    med = execute_one("SELECT user_id FROM medicines WHERE id = ?", (med_id,))
    if not med:
        return False
        
    if not check_parent_access(current_user, med["user_id"]):
        raise PermissionError("Unauthorized deletion of medicine schedule.")
        
    count = execute_update("DELETE FROM medicines WHERE id = ?", (med_id,))
    if count > 0:
        log_audit(
            actor_id=current_user["id"],
            target_id=med["user_id"],
            action="MEDICINE_DELETED",
            resource_type="medicines",
            resource_id=str(med_id)
        )
        return True
    return False

def get_user_medicines(user_id: int, current_user: Dict[str, Any], active_only: bool = True) -> List[Dict[str, Any]]:
    """Retrieves medicine schedules for a user."""
    if not check_parent_access(current_user, user_id):
        raise PermissionError("Unauthorized access to user medicines.")
        
    sql = "SELECT * FROM medicines WHERE user_id = ?"
    params = [user_id]
    if active_only:
        sql += " AND is_active = 1"
    sql += " ORDER BY name ASC"
    
    rows = execute_query(sql, tuple(params))
    medicines = []
    for r in rows:
        d = dict(r)
        try:
            d["timing_slots"] = json.loads(d["timing_slots"])
        except Exception:
            d["timing_slots"] = [s.strip() for s in d["timing_slots"].split(",") if s.strip()]
        medicines.append(d)
    return medicines

def log_dose(
    user_id: int,
    medicine_id: int,
    slot: str,
    scheduled_date: str,
    status: str,
    current_user: Dict[str, Any],
    notes: Optional[str] = None
) -> bool:
    """
    Logs or updates a dose status ('taken', 'skipped', 'missed').
    Prevents duplicate dose records using SQLite ON CONFLICT UPSERT.
    Allows correcting accidental entries.
    """
    if not check_parent_access(current_user, user_id):
        raise PermissionError("Unauthorized dose logging.")
        
    slot_clean = slot.strip().lower()
    if slot_clean not in ("morning", "afternoon", "night"):
        raise ValueError("Invalid time slot. Must be morning, afternoon, or night.")
        
    status_clean = status.strip().lower()
    if status_clean not in ("taken", "skipped", "missed"):
        raise ValueError("Invalid status. Must be taken, skipped, or missed.")
        
    execute_insert("""
        INSERT INTO dose_logs (user_id, medicine_id, slot, scheduled_date, status, logged_by, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, medicine_id, scheduled_date, slot)
        DO UPDATE SET
            status = excluded.status,
            logged_at = CURRENT_TIMESTAMP,
            logged_by = excluded.logged_by,
            notes = excluded.notes;
    """, (user_id, medicine_id, slot_clean, scheduled_date, status_clean, current_user["id"], notes))
    
    log_audit(
        actor_id=current_user["id"],
        target_id=user_id,
        action="DOSE_LOGGED",
        resource_type="dose_logs",
        resource_id=f"{medicine_id}:{scheduled_date}:{slot_clean}"
    )
    return True

def get_daily_schedule_with_logs(user_id: int, target_date_str: str, current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns all scheduled doses for a specific date (YYYY-MM-DD) combined with current logging status.
    """
    if not check_parent_access(current_user, user_id):
        raise PermissionError("Unauthorized access to schedule.")
        
    medicines = get_user_medicines(user_id, current_user, active_only=True)
    
    # Query all logs for this date
    logs = execute_query("""
        SELECT medicine_id, slot, status, logged_at, notes
        FROM dose_logs
        WHERE user_id = ? AND scheduled_date = ?
    """, (user_id, target_date_str))
    
    logs_lookup = {(r["medicine_id"], r["slot"]): dict(r) for r in logs}
    
    schedule_items = []
    for med in medicines:
        for slot in med["timing_slots"]:
            key = (med["id"], slot)
            log_info = logs_lookup.get(key)
            status = log_info["status"] if log_info else "pending"
            schedule_items.append({
                "medicine_id": med["id"],
                "medicine_name": med["name"],
                "dose": med["dose"],
                "food_instruction": med["food_instruction"],
                "slot": slot,
                "scheduled_date": target_date_str,
                "status": status,
                "logged_at": log_info["logged_at"] if log_info else None,
                "notes": log_info["notes"] if log_info else None
            })
            
    # Sort slots chronologically: morning, afternoon, night
    slot_order = {"morning": 1, "afternoon": 2, "night": 3}
    schedule_items.sort(key=lambda x: (slot_order.get(x["slot"], 99), x["medicine_name"]))
    return schedule_items

def get_adherence_stats(user_id: int, days: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates adherence statistics over the past N days.
    """
    if not check_parent_access(current_user, user_id):
        raise PermissionError("Unauthorized access to adherence statistics.")
        
    start_date = (date.today() - timedelta(days=days)).isoformat()
    end_date = date.today().isoformat()
    
    rows = execute_query("""
        SELECT status, COUNT(*) as count
        FROM dose_logs
        WHERE user_id = ? AND scheduled_date BETWEEN ? AND ?
        GROUP BY status
    """, (user_id, start_date, end_date))
    
    counts = {"taken": 0, "skipped": 0, "missed": 0}
    for r in rows:
        counts[r["status"]] = r["count"]
        
    total_logged = sum(counts.values())
    rate = (counts["taken"] / total_logged * 100) if total_logged > 0 else 0.0
    
    return {
        "period_days": days,
        "taken": counts["taken"],
        "skipped": counts["skipped"],
        "missed": counts["missed"],
        "total": total_logged,
        "adherence_rate": round(rate, 1)
    }
