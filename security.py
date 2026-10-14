import os
import re
import time
import uuid
import hashlib
from typing import Tuple, Optional, Dict
import bcrypt
from cryptography.fernet import Fernet, InvalidToken

from config import FERNET_KEY, MAX_FILE_SIZE_MB, UPLOAD_DIR

# Initialize Fernet cipher suite
_fernet = Fernet(FERNET_KEY.encode("utf-8") if isinstance(FERNET_KEY, str) else FERNET_KEY)

# ----------------- Encryption / Decryption -----------------
def encrypt_text(plaintext: str) -> str:
    """Encrypt a plaintext string and return a base64-encoded encrypted token string."""
    if not plaintext:
        return ""
    token_bytes = _fernet.encrypt(plaintext.encode("utf-8"))
    return token_bytes.decode("utf-8")

def decrypt_text(ciphertext: str) -> str:
    """Decrypt a base64-encoded encrypted token string back to plaintext."""
    if not ciphertext:
        return ""
    try:
        decrypted_bytes = _fernet.decrypt(ciphertext.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except (InvalidToken, Exception):
        # Return fallback or raise depending on usage
        return "[Decryption Error: Invalid Key or Tampered Data]"

def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt raw bytes."""
    if not data:
        return b""
    return _fernet.encrypt(data)

def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt raw bytes."""
    if not data:
        return b""
    return _fernet.decrypt(data)

# ----------------- Password Hashing -----------------
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

# ----------------- Input Validation -----------------
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    if not email or len(email.strip()) > 254:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def is_valid_password(password: str) -> Tuple[bool, str]:
    """Validate password requirements (at least 8 chars)."""
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    return True, ""

# ----------------- Login Rate Limiting -----------------
# In-memory rate limiting store: identifier -> [timestamp1, timestamp2, ...]
_login_attempts: Dict[str, list] = {}
RATE_LIMIT_WINDOW_SECONDS = 300  # 5 minutes
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 600  # 10 minutes

def is_rate_limited(identifier: str) -> Tuple[bool, int]:
    """Check if identifier is rate limited. Returns (is_limited, remaining_lockout_seconds)."""
    key = identifier.strip().lower()
    now = time.time()
    
    if key not in _login_attempts:
        return False, 0
    
    # Filter attempts within window or lockout
    attempts = [t for t in _login_attempts[key] if now - t < LOCKOUT_SECONDS]
    _login_attempts[key] = attempts
    
    if len(attempts) >= MAX_FAILED_ATTEMPTS:
        last_attempt = max(attempts)
        elapsed = now - last_attempt
        remaining = int(LOCKOUT_SECONDS - elapsed)
        if remaining > 0:
            return True, remaining
    return False, 0

def record_login_attempt(identifier: str, success: bool):
    """Record a login attempt. Reset on success, append timestamp on failure."""
    key = identifier.strip().lower()
    now = time.time()
    if success:
        if key in _login_attempts:
            del _login_attempts[key]
    else:
        if key not in _login_attempts:
            _login_attempts[key] = []
        _login_attempts[key].append(now)

# ----------------- Secure File Handling -----------------
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

MAGIC_NUMBERS = {
    b"%PDF": ".pdf",
    b"\x89PNG\r\n\x1a\n": ".png",
    b"\xff\xd8\xff": ".jpg",
}

def validate_uploaded_file(file_name: str, file_bytes: bytes) -> Tuple[bool, str]:
    """
    Validate file extension, size, and magic bytes.
    Protects against malicious file uploads and MIME spoofing.
    """
    if not file_bytes:
        return False, "Uploaded file is empty."
    
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File exceeds maximum allowed size of {MAX_FILE_SIZE_MB}MB (current: {size_mb:.2f}MB)."
    
    # Check extension
    _, ext = os.path.splitext(file_name.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Supported formats: PDF, PNG, JPG, JPEG."
    
    # Check magic signature
    has_valid_signature = False
    for signature, sig_ext in MAGIC_NUMBERS.items():
        if file_bytes.startswith(signature):
            if sig_ext == ".jpg" and ext in [".jpg", ".jpeg"]:
                has_valid_signature = True
                break
            elif sig_ext == ext:
                has_valid_signature = True
                break
    
    if not has_valid_signature:
        return False, "File content header does not match expected image or PDF format."
    
    return True, ""

def save_uploaded_file_securely(original_name: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Saves file with a random UUID server-side filename in UPLOAD_DIR.
    Returns (saved_file_path, file_sha256_hash).
    """
    _, ext = os.path.splitext(original_name.lower())
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    saved_path = UPLOAD_DIR / safe_filename
    
    # Calculate SHA-256 for file integrity tracking
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # Write bytes to disk
    with open(saved_path, "wb") as f:
        f.write(file_bytes)
    
    return str(saved_path), sha256_hash
