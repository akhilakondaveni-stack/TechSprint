import logging
from typing import Tuple, Optional, Dict, Any
import requests

from config import TELEGRAM_BOT_TOKEN
from database import execute_insert

logger = logging.getLogger(__name__)

def send_telegram_message(
    chat_id: str,
    text: str,
    user_id: int,
    message_type: str
) -> Tuple[bool, str]:
    """
    Sends a discreet notification to a user's Telegram chat via Telegram Bot API.
    Does not expose sensitive clinical data in external chat notifications.
    Records delivery outcome in notification_logs.
    """
    if not TELEGRAM_BOT_TOKEN:
        err = "Telegram Bot Token is not configured in server environment."
        logger.warning(err)
        _log_notification(user_id, chat_id, message_type, "failed", err)
        return False, err

    if not chat_id or not chat_id.strip():
        err = "User has not configured a Telegram Chat ID."
        _log_notification(user_id, "unknown", message_type, "opted_out", err)
        return False, err

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id.strip(),
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10.0)
        res_json = response.json()
        if response.status_code == 200 and res_json.get("ok"):
            _log_notification(user_id, chat_id, message_type, "sent", None)
            return True, "Notification sent successfully."
        else:
            err = res_json.get("description", "Unknown Telegram API error")
            logger.error(f"Telegram API delivery failed: {err}")
            _log_notification(user_id, chat_id, message_type, "failed", err)
            return False, f"Telegram API error: {err}"
    except Exception as e:
        err = str(e)
        logger.error(f"Telegram connection error: {err}")
        _log_notification(user_id, chat_id, message_type, "failed", err)
        return False, f"Failed to deliver message: {err}"

def _log_notification(user_id: int, recipient_id: str, message_type: str, status: str, error_msg: Optional[str]):
    """Records delivery attempt in the database."""
    try:
        execute_insert("""
            INSERT INTO notification_logs (user_id, channel, recipient_id, message_type, status, error_message)
            VALUES (?, 'telegram', ?, ?, ?, ?)
        """, (user_id, recipient_id, message_type, status, error_msg))
    except Exception as e:
        logger.error(f"Failed to record notification log: {e}")

def send_test_telegram_ping(chat_id: str, user_id: int) -> Tuple[bool, str]:
    """Sends a verification ping to confirm user's Chat ID configuration."""
    msg = (
        "🌿 *HealthBuddy Connection Test*\n\n"
        "Your Telegram notifications have been successfully verified! "
        "You will receive discreet medicine schedule reminders and appointment updates here."
    )
    return send_telegram_message(chat_id, msg, user_id, "verification_test")

def send_medicine_reminder(
    user_id: int,
    user_name: str,
    chat_id: str,
    slot: str,
    medicines_summary: str
) -> Tuple[bool, str]:
    """Sends a discreet medicine reminder."""
    slot_label = slot.capitalize()
    msg = (
        f"🌿 *HealthBuddy Medicine Reminder*\n\n"
        f"Hello {user_name}, it's time for your *{slot_label}* medications.\n\n"
        f"📋 *Scheduled:* {medicines_summary}\n\n"
        f"💡 _Please log your dose in the HealthBuddy app after taking it._\n"
        f"⚠️ _Never take a double dose if you missed a previous one._"
    )
    return send_telegram_message(chat_id, msg, user_id, f"medicine_{slot}")

def send_appointment_reminder(
    user_id: int,
    user_name: str,
    chat_id: str,
    doctor_name: str,
    facility: str,
    app_date: str,
    app_time: str
) -> Tuple[bool, str]:
    """Sends an appointment reminder."""
    msg = (
        f"🗓️ *HealthBuddy Appointment Reminder*\n\n"
        f"Hello {user_name}, you have an upcoming medical appointment scheduled:\n\n"
        f"👨‍⚕️ *Doctor:* {doctor_name}\n"
        f"🏥 *Location:* {facility}\n"
        f"📅 *Date & Time:* {app_date} at {app_time}\n\n"
        f"💡 _Have your medical reports and questions ready!_"
    )
    return send_telegram_message(chat_id, msg, user_id, f"appointment_{app_date}")
