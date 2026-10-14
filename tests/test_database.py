import pytest
import sqlite3
from database import init_db, get_connection, execute_query, execute_one, log_audit

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()

def test_database_foreign_key_enforcement():
    conn = get_connection()
    # Try inserting a medicine for a nonexistent user_id
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("""
            INSERT INTO medicines (user_id, name, dose, frequency, timing_slots, food_instruction)
            VALUES (999999, 'Phantom Med', '10mg', 'Daily', '["morning"]', 'After Food')
        """)
    conn.close()

def test_schema_version_tracked():
    row = execute_one("SELECT version FROM schema_version WHERE version = 1")
    assert row is not None
    assert row["version"] == 1

def test_audit_logging():
    log_audit(actor_id=1, target_id=1, action="TEST_AUDIT_ACTION", resource_type="test_resource", resource_id="123")
    row = execute_one("SELECT * FROM audit_logs WHERE action = 'TEST_AUDIT_ACTION' ORDER BY id DESC LIMIT 1")
    assert row is not None
    assert row["action"] == "TEST_AUDIT_ACTION"
    assert row["resource_type"] == "test_resource"
