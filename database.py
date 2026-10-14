import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple
from config import SQLITE_PATH

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 1

def get_connection() -> sqlite3.Connection:
    """Creates and returns a SQLite connection with row_factory enabled and foreign keys enforced."""
    conn = sqlite3.connect(SQLITE_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

@contextmanager
def get_db():
    """Context manager for safe database transactions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error occurred, rolled back: {e}")
        raise e
    finally:
        conn.close()

def init_db():
    """Initializes database tables, indexes, and schema version."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Schema version table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('parent', 'child')),
                phone TEXT,
                preferred_lang TEXT DEFAULT 'en' CHECK(preferred_lang IN ('en', 'hi', 'te')),
                telegram_chat_id TEXT,
                notify_medicines INTEGER DEFAULT 1,
                notify_appointments INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Family links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS family_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                child_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                invite_code TEXT UNIQUE NOT NULL,
                relationship TEXT DEFAULT 'Child',
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'revoked')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Medical reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                report_date TEXT NOT NULL,
                doctor_name TEXT,
                facility_name TEXT,
                report_type TEXT DEFAULT 'Lab Report',
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                extracted_data_encrypted TEXT NOT NULL,
                explanation_encrypted TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Medicines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                dose TEXT NOT NULL,
                frequency TEXT NOT NULL,
                timing_slots TEXT NOT NULL,
                food_instruction TEXT NOT NULL DEFAULT 'After Food',
                duration TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Dose logs table with UNIQUE constraint to prevent duplicate entries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dose_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                medicine_id INTEGER NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
                slot TEXT NOT NULL CHECK(slot IN ('morning', 'afternoon', 'night')),
                scheduled_date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('taken', 'skipped', 'missed')),
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logged_by INTEGER REFERENCES users(id),
                notes TEXT,
                UNIQUE(user_id, medicine_id, scheduled_date, slot)
            );
        """)
        
        # Appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                doctor_name TEXT NOT NULL,
                facility TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                contact_number TEXT,
                mode TEXT DEFAULT 'In-Person',
                status TEXT DEFAULT 'upcoming' CHECK(status IN ('upcoming', 'completed', 'cancelled')),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Symptoms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                symptom_name TEXT NOT NULL,
                severity TEXT NOT NULL CHECK(severity IN ('mild', 'moderate', 'severe')),
                notes TEXT,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Notification logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                channel TEXT NOT NULL DEFAULT 'telegram',
                recipient_id TEXT,
                message_type TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('sent', 'failed', 'opted_out')),
                error_message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Audit logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                target_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Monthly summaries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                month_year TEXT NOT NULL,
                summary_pdf_path TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Indexes for query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_medical_reports_user ON medical_reports(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_medicines_user ON medicines(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dose_logs_lookup ON dose_logs(user_id, scheduled_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_family_links_parent ON family_links(parent_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_family_links_child ON family_links(child_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_family_links_code ON family_links(invite_code);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_appointments_user ON appointments(user_id, appointment_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_actor ON audit_logs(actor_user_id);")
        
        # Check and record schema version
        cursor.execute("SELECT version FROM schema_version WHERE version = ?", (CURRENT_SCHEMA_VERSION,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (CURRENT_SCHEMA_VERSION,))

def execute_query(sql: str, params: Tuple = ()) -> List[sqlite3.Row]:
    """Execute a read query and return rows."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

def execute_one(sql: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
    """Execute a query expecting a single row result."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()

def execute_insert(sql: str, params: Tuple = ()) -> int:
    """Execute an INSERT query and return the lastrowid."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.lastrowid

def execute_update(sql: str, params: Tuple = ()) -> int:
    """Execute an UPDATE or DELETE query and return the rowcount."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.rowcount

def log_audit(actor_id: Optional[int], target_id: Optional[int], action: str, resource_type: str, resource_id: Optional[str] = None, ip_address: Optional[str] = "127.0.0.1"):
    """Record an audit trail event for security compliance."""
    try:
        execute_insert("""
            INSERT INTO audit_logs (actor_user_id, target_user_id, action, resource_type, resource_id, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (actor_id, target_id, action, resource_type, str(resource_id) if resource_id else None, ip_address))
    except Exception as e:
        logger.error(f"Failed to record audit log: {e}")
