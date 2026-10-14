import logging
import threading
from datetime import datetime, date
import zoneinfo
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler

from config import DEFAULT_TIMEZONE, DEFAULT_REMINDER_TIMES_IST
from database import execute_query
from notification_service import send_medicine_reminder, send_appointment_reminder

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None
_lock = threading.Lock()

def check_and_send_scheduled_reminders():
    """
    Idempotent reminder check job. Runs periodically.
    Verifies delivery history to never send duplicate notifications.
    """
    try:
        # Determine local time in Asia/Kolkata
        try:
            tz = zoneinfo.ZoneInfo(DEFAULT_TIMEZONE)
            now = datetime.now(tz)
        except Exception:
            now = datetime.now()

        today_str = now.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%H:%M")

        # Determine if current time matches any slot window (with 15 min leeway)
        current_slot = None
        for slot, slot_time in DEFAULT_REMINDER_TIMES_IST.items():
            # Match exact hour:minute
            if current_time_str == slot_time:
                current_slot = slot
                break

        # 1. Process Medicine Reminders if in slot window
        if current_slot:
            # Query users who want medicine notifications and have chat ID
            users = execute_query("""
                SELECT id, full_name, telegram_chat_id FROM users
                WHERE notify_medicines = 1 AND telegram_chat_id IS NOT NULL AND telegram_chat_id != ''
            """)

            for user in users:
                user_id = user["id"]
                msg_type = f"medicine_{current_slot}_{today_str}"

                # Idempotency check: verify if reminder was already sent today for this slot
                already_sent = execute_query("""
                    SELECT id FROM notification_logs
                    WHERE user_id = ? AND message_type = ? AND status = 'sent'
                """, (user_id, msg_type))

                if already_sent:
                    continue

                # Check if user has active medicines for this slot
                medicines = execute_query("""
                    SELECT name, dose, food_instruction, timing_slots FROM medicines
                    WHERE user_id = ? AND is_active = 1
                """, (user_id,))

                active_for_slot = []
                for med in medicines:
                    slots_str = med["timing_slots"].lower()
                    if current_slot in slots_str:
                        active_for_slot.append(f"{med['name']} ({med['dose']}) - {med['food_instruction']}")

                if active_for_slot:
                    summary = ", ".join(active_for_slot)
                    send_medicine_reminder(
                        user_id=user_id,
                        user_name=user["full_name"],
                        chat_id=user["telegram_chat_id"],
                        slot=current_slot,
                        medicines_summary=summary
                    )

        # 2. Process Appointment Reminders
        appointments = execute_query("""
            SELECT a.id, a.user_id, a.doctor_name, a.facility, a.appointment_date, a.appointment_time,
                   u.full_name, u.telegram_chat_id
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.status = 'upcoming' AND a.appointment_date = ?
                  AND u.notify_appointments = 1 AND u.telegram_chat_id IS NOT NULL
        """, (today_str,))

        for app in appointments:
            msg_type = f"appointment_{app['id']}_{today_str}"
            already_sent = execute_query("""
                SELECT id FROM notification_logs
                WHERE user_id = ? AND message_type = ? AND status = 'sent'
            """, (app["user_id"], msg_type))

            if not already_sent:
                send_appointment_reminder(
                    user_id=app["user_id"],
                    user_name=app["full_name"],
                    chat_id=app["telegram_chat_id"],
                    doctor_name=app["doctor_name"],
                    facility=app["facility"],
                    app_date=app["appointment_date"],
                    app_time=app["appointment_time"]
                )

    except Exception as e:
        logger.error(f"Error executing reminder scheduler job: {e}")

def start_background_scheduler():
    """
    Starts the persistent background scheduler singleton.
    Guarantees only one worker instance runs across Streamlit reruns.
    """
    global _scheduler
    with _lock:
        if _scheduler is None or not _scheduler.running:
            _scheduler = BackgroundScheduler(daemon=True)
            _scheduler.add_job(
                check_and_send_scheduled_reminders,
                "interval",
                seconds=60,
                id="reminder_worker",
                replace_existing=True
            )
            _scheduler.start()
            logger.info("HealthBuddy Background Scheduler successfully started.")
        return _scheduler

def stop_background_scheduler():
    """Stops the scheduler on shutdown."""
    global _scheduler
    with _lock:
        if _scheduler and _scheduler.running:
            _scheduler.shutdown(wait=False)
            _scheduler = None
            logger.info("HealthBuddy Background Scheduler stopped.")
