import json
import logging
from datetime import date, timedelta
from database import execute_one, execute_insert
from security import hash_password, encrypt_text
from ai_service import get_synthetic_report_data

logger = logging.getLogger(__name__)

def seed_sample_data_if_empty():
    """
    Seeds initial demo data if the users table is completely empty.
    Creates:
    - 1 Parent user: parent@healthbuddy.com (Password: Password123!)
    - 1 Child user: child@healthbuddy.com (Password: Password123!)
    - An approved family link between them
    - Sample medicines and dose logs
    - Sample medical reports
    - Sample appointments
    """
    existing_user = execute_one("SELECT id FROM users LIMIT 1")
    if existing_user:
        return  # Database already seeded or populated

    try:
        # 1. Create Parent User
        p_pw = hash_password("Password123!")
        parent_id = execute_insert("""
            INSERT INTO users (email, password_hash, full_name, role, phone, preferred_lang, notify_medicines, notify_appointments)
            VALUES (?, ?, ?, 'parent', '+91 98765 43210', 'en', 1, 1)
        """, ("parent@healthbuddy.com", p_pw, "Ramachandra Rao",))

        # 2. Create Child User
        c_pw = hash_password("Password123!")
        child_id = execute_insert("""
            INSERT INTO users (email, password_hash, full_name, role, phone, preferred_lang, notify_medicines, notify_appointments)
            VALUES (?, ?, ?, 'child', '+91 91234 56789', 'en', 1, 1)
        """, ("child@healthbuddy.com", c_pw, "Kavita Rao",))

        # 3. Create Approved Family Link
        execute_insert("""
            INSERT INTO family_links (parent_id, child_id, invite_code, relationship, status, approved_at)
            VALUES (?, ?, 'HB-WELCOME', 'Daughter', 'approved', CURRENT_TIMESTAMP)
        """, (parent_id, child_id))

        # 4. Create Sample Medicines for Parent
        m1 = execute_insert("""
            INSERT INTO medicines (user_id, name, dose, frequency, timing_slots, food_instruction, duration, is_active)
            VALUES (?, 'Metformin Glycomet', '500 mg', 'Twice daily', '["morning", "night"]', 'After Food', 'Ongoing', 1)
        """, (parent_id,))

        m2 = execute_insert("""
            INSERT INTO medicines (user_id, name, dose, frequency, timing_slots, food_instruction, duration, is_active)
            VALUES (?, 'Telmisartan Telma', '40 mg', 'Once daily', '["morning"]', 'Before Food', 'Ongoing', 1)
        """, (parent_id,))

        m3 = execute_insert("""
            INSERT INTO medicines (user_id, name, dose, frequency, timing_slots, food_instruction, duration, is_active)
            VALUES (?, 'Atorvastatin Lipitor', '10 mg', 'Once daily', '["night"]', 'After Food', 'Ongoing', 1)
        """, (parent_id,))

        # 5. Create Dose Logs for past 3 days
        today = date.today()
        for i in range(3):
            d_str = (today - timedelta(days=i)).isoformat()
            execute_insert("""
                INSERT OR IGNORE INTO dose_logs (user_id, medicine_id, slot, scheduled_date, status, logged_by, notes)
                VALUES (?, ?, 'morning', ?, 'taken', ?, 'Taken with breakfast')
            """, (parent_id, m1, d_str, parent_id))

            execute_insert("""
                INSERT OR IGNORE INTO dose_logs (user_id, medicine_id, slot, scheduled_date, status, logged_by, notes)
                VALUES (?, ?, 'morning', ?, 'taken', ?, 'Taken on schedule')
            """, (parent_id, m2, d_str, parent_id))

            execute_insert("""
                INSERT OR IGNORE INTO dose_logs (user_id, medicine_id, slot, scheduled_date, status, logged_by, notes)
                VALUES (?, ?, 'night', ?, 'taken', ?, 'Taken after dinner')
            """, (parent_id, m3, d_str, parent_id))

        # 6. Create Sample Medical Report
        synthetic = get_synthetic_report_data(language="en")
        raw_data = synthetic.model_dump()
        enc_data = encrypt_text(json.dumps(raw_data))
        enc_expl = encrypt_text(json.dumps({
            "summary": synthetic.summary,
            "doctor_questions": synthetic.doctor_questions,
            "food_tips": synthetic.food_tips,
            "disclaimer": synthetic.disclaimer
        }))

        execute_insert("""
            INSERT INTO medical_reports (
                user_id, title, report_date, doctor_name, facility_name,
                report_type, file_path, file_hash,
                extracted_data_encrypted, explanation_encrypted
            ) VALUES (?, 'Complete Blood & Lipid Profile', ?, 'Dr. S. K. Sharma', 'Apollo Diagnostics', 'Blood Test', 'data/sample_report.pdf', 'sample_hash_demo', ?, ?)
        """, (parent_id, (today - timedelta(days=10)).isoformat(), enc_data, enc_expl))

        # 7. Create Sample Appointments
        execute_insert("""
            INSERT INTO appointments (
                user_id, doctor_name, facility, appointment_date, appointment_time,
                contact_number, mode, status, notes
            ) VALUES (?, 'Dr. S. K. Sharma (Cardiologist)', 'Apollo Hospital, Banjara Hills', ?, '10:30', '+91 98480 12345', 'In-Person', 'upcoming', 'Quarterly routine review of blood pressure and lipids.')
        """, (parent_id, (today + timedelta(days=4)).isoformat()))

        execute_insert("""
            INSERT INTO appointments (
                user_id, doctor_name, facility, appointment_date, appointment_time,
                contact_number, mode, status, notes
            ) VALUES (?, 'Dr. Meenakshi Rao (Ophthalmologist)', 'L V Prasad Eye Institute', ?, '15:00', '+91 98490 67890', 'In-Person', 'completed', 'Annual diabetic retinopathy screening - normal.')
        """, (parent_id, (today - timedelta(days=20)).isoformat()))

        logger.info("Sample seed data created successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
