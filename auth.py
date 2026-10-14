import logging
from typing import Optional, Dict, Any, Tuple
from database import execute_one, execute_insert, execute_update, log_audit
from security import (
    hash_password,
    verify_password,
    is_valid_email,
    is_valid_password,
    is_rate_limited,
    record_login_attempt,
)

logger = logging.getLogger(__name__)

def register_user(
    email: str,
    password: str,
    full_name: str,
    role: str = "parent",
    phone: Optional[str] = None,
    preferred_lang: str = "en"
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Registers a new user account with validated input and hashed credentials.
    Roles: 'parent' or 'child'.
    """
    email_clean = email.strip().lower()
    full_name_clean = full_name.strip()
    
    if not is_valid_email(email_clean):
        return False, "Please provide a valid email address.", None
    
    valid_pass, pass_err = is_valid_password(password)
    if not valid_pass:
        return False, pass_err, None
    
    if not full_name_clean:
        return False, "Full name is required.", None
    
    if role not in ("parent", "child"):
        return False, "Invalid account role. Must be 'parent' or 'child'.", None
    
    # Check if user already exists
    existing = execute_one("SELECT id FROM users WHERE email = ?", (email_clean,))
    if existing:
        return False, "An account with this email address already exists. Please log in.", None
    
    password_hashed = hash_password(password)
    
    try:
        user_id = execute_insert("""
            INSERT INTO users (email, password_hash, full_name, role, phone, preferred_lang)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (email_clean, password_hashed, full_name_clean, role, phone.strip() if phone else None, preferred_lang))
        
        log_audit(actor_id=user_id, target_id=user_id, action="USER_REGISTERED", resource_type="users", resource_id=str(user_id))
        
        user_data = get_user_by_id(user_id)
        return True, "Account created successfully!", user_data
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return False, "An unexpected error occurred while creating your account.", None

def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticates user with rate limiting check and bcrypt password verification.
    """
    email_clean = email.strip().lower()
    
    # Rate limit check
    rate_limited, lockout_remaining = is_rate_limited(email_clean)
    if rate_limited:
        return False, f"Too many failed login attempts. Please try again in {lockout_remaining} seconds.", None
    
    user_row = execute_one("""
        SELECT id, email, password_hash, full_name, role, phone, preferred_lang,
               telegram_chat_id, notify_medicines, notify_appointments, created_at
        FROM users WHERE email = ?
    """, (email_clean,))
    
    if not user_row:
        record_login_attempt(email_clean, success=False)
        return False, "Invalid email or password.", None
    
    if not verify_password(password, user_row["password_hash"]):
        record_login_attempt(email_clean, success=False)
        return False, "Invalid email or password.", None
    
    # Successful login
    record_login_attempt(email_clean, success=True)
    user_dict = dict(user_row)
    del user_dict["password_hash"]
    
    log_audit(actor_id=user_dict["id"], target_id=user_dict["id"], action="USER_LOGIN", resource_type="users", resource_id=str(user_dict["id"]))
    
    return True, "Login successful!", user_dict

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user details by user ID (omits password hash)."""
    user_row = execute_one("""
        SELECT id, email, full_name, role, phone, preferred_lang,
               telegram_chat_id, notify_medicines, notify_appointments, created_at
        FROM users WHERE id = ?
    """, (user_id,))
    return dict(user_row) if user_row else None

def update_user_profile(
    user_id: int,
    full_name: str,
    phone: Optional[str],
    preferred_lang: str,
    telegram_chat_id: Optional[str],
    notify_medicines: bool,
    notify_appointments: bool
) -> bool:
    """Updates user preferences and contact details."""
    count = execute_update("""
        UPDATE users
        SET full_name = ?, phone = ?, preferred_lang = ?, telegram_chat_id = ?,
            notify_medicines = ?, notify_appointments = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        full_name.strip(),
        phone.strip() if phone else None,
        preferred_lang,
        telegram_chat_id.strip() if telegram_chat_id else None,
        1 if notify_medicines else 0,
        1 if notify_appointments else 0,
        user_id
    ))
    if count > 0:
        log_audit(actor_id=user_id, target_id=user_id, action="PROFILE_UPDATED", resource_type="users", resource_id=str(user_id))
        return True
    return False

def check_parent_access(current_user: Dict[str, Any], target_parent_id: int) -> bool:
    """
    Enforces server-side authorization check.
    Returns True if current_user is either:
      1. The parent themselves (target_parent_id == current_user['id'])
      2. An approved family member (status == 'approved' in family_links)
    """
    if not current_user or not target_parent_id:
        return False
    
    user_id = current_user["id"]
    if user_id == target_parent_id:
        return True
    
    # Check if approved child
    link = execute_one("""
        SELECT id FROM family_links
        WHERE parent_id = ? AND child_id = ? AND status = 'approved'
    """, (target_parent_id, user_id))
    
    return bool(link)
