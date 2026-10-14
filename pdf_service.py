import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from config import SUMMARIES_DIR
from auth import check_parent_access, get_user_by_id
from database import execute_query, execute_insert, log_audit
from security import decrypt_text

logger = logging.getLogger(__name__)

PDF_DISCLAIMER = (
    "NOTICE: This monthly summary report is generated automatically by HealthBuddy for informational, "
    "archival, and discussion purposes with your qualified healthcare provider. "
    "This document does not constitute a clinical diagnosis or treatment prescription. "
    "Do not modify, pause, or discontinue prescribed medications without medical advice."
)

def generate_monthly_health_summary_pdf(
    user_id: int,
    month_year: str,  # format 'YYYY-MM'
    current_user: Dict[str, Any]
) -> str:
    """
    Generates a professional, beautifully styled monthly health summary PDF.
    Validates user authorization before compiling patient records.
    Returns the file path of the generated PDF.
    """
    if not check_parent_access(current_user, user_id):
        raise PermissionError("Unauthorized access to generate health summary.")

    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("Target user profile not found.")

    filename = f"HealthBuddy_Summary_{user_id}_{month_year.replace('-', '')}.pdf"
    pdf_path = SUMMARIES_DIR / filename

    # Query medical reports in month
    reports = execute_query("""
        SELECT title, report_date, doctor_name, facility_name, report_type, extracted_data_encrypted
        FROM medical_reports
        WHERE user_id = ? AND strftime('%Y-%m', report_date) = ?
        ORDER BY report_date ASC
    """, (user_id, month_year))

    # Query medicines
    medicines = execute_query("""
        SELECT name, dose, frequency, food_instruction, duration, is_active
        FROM medicines
        WHERE user_id = ?
        ORDER BY name ASC
    """, (user_id,))

    # Query adherence for that month
    adherence_rows = execute_query("""
        SELECT status, COUNT(*) as count
        FROM dose_logs
        WHERE user_id = ? AND strftime('%Y-%m', scheduled_date) = ?
        GROUP BY status
    """, (user_id, month_year))

    adh_counts = {"taken": 0, "skipped": 0, "missed": 0}
    for r in adherence_rows:
        adh_counts[r["status"]] = r["count"]
    total_doses = sum(adh_counts.values())
    adherence_pct = (adh_counts["taken"] / total_doses * 100) if total_doses > 0 else 0.0

    # Query appointments in month
    appointments = execute_query("""
        SELECT doctor_name, facility, appointment_date, appointment_time, mode, status
        FROM appointments
        WHERE user_id = ? AND strftime('%Y-%m', appointment_date) = ?
        ORDER BY appointment_date ASC
    """, (user_id, month_year))

    # Build ReportLab Document
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F766E'),
        spaceBefore=10,
        spaceAfter=6
    )
    normal_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1F2937')
    )
    bold_style = ParagraphStyle(
        'BodyTextBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#111827')
    )
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#6B7280')
    )

    story = []

    # Header
    story.append(Paragraph("🌿 HealthBuddy for Parents — Monthly Health Summary", title_style))
    story.append(Paragraph(
        f"<b>Patient:</b> {user['full_name']} &nbsp;|&nbsp; <b>Report Period:</b> {month_year} &nbsp;|&nbsp; "
        f"<b>Generated:</b> {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))

    # 1. Executive Adherence Summary Box
    story.append(Paragraph("1. Medicine Adherence Summary", heading_style))
    adh_data = [
        [
            Paragraph(f"<b>Overall Adherence Rate:</b> {adherence_pct:.1f}%", bold_style),
            Paragraph(f"<b>Taken Doses:</b> {adh_counts['taken']}", normal_style),
            Paragraph(f"<b>Skipped Doses:</b> {adh_counts['skipped']}", normal_style),
            Paragraph(f"<b>Missed Doses:</b> {adh_counts['missed']}", normal_style)
        ]
    ]
    adh_table = Table(adh_data, colWidths=[180, 120, 120, 120])
    adh_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0FDF4')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#86EFAC')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(adh_table)
    story.append(Spacer(1, 10))

    # 2. Active Medications
    story.append(Paragraph("2. Prescribed Medications", heading_style))
    if medicines:
        med_rows = [[
            Paragraph("<b>Medicine</b>", bold_style),
            Paragraph("<b>Dose & Frequency</b>", bold_style),
            Paragraph("<b>Food Instruction</b>", bold_style),
            Paragraph("<b>Duration / Status</b>", bold_style)
        ]]
        for m in medicines:
            status_text = "Active" if m["is_active"] else "Inactive"
            med_rows.append([
                Paragraph(m["name"], normal_style),
                Paragraph(f"{m['dose']}, {m['frequency']}", normal_style),
                Paragraph(m["food_instruction"], normal_style),
                Paragraph(f"{m['duration'] or 'Ongoing'} ({status_text})", normal_style)
            ])
        med_table = Table(med_rows, colWidths=[150, 150, 120, 120])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0F2FE')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(med_table)
    else:
        story.append(Paragraph("No active medications recorded for this period.", normal_style))
    story.append(Spacer(1, 10))

    # 3. Medical Reports in Month
    story.append(Paragraph("3. Medical Reports & Diagnostic Tests", heading_style))
    if reports:
        rep_rows = [[
            Paragraph("<b>Date</b>", bold_style),
            Paragraph("<b>Report Title</b>", bold_style),
            Paragraph("<b>Facility / Doctor</b>", bold_style),
            Paragraph("<b>Key Test Highlights</b>", bold_style)
        ]]
        for r in reports:
            highlights = "None recorded"
            try:
                decrypted = decrypt_text(r["extracted_data_encrypted"])
                if decrypted:
                    data = json.loads(decrypted)
                    tests = data.get("tests", [])
                    if tests:
                        notable = [f"{t['name']}: {t['value']} {t.get('unit','')}" for t in tests[:3]]
                        highlights = ", ".join(notable)
            except Exception:
                pass

            rep_rows.append([
                Paragraph(r["report_date"], normal_style),
                Paragraph(r["title"], normal_style),
                Paragraph(f"{r['facility_name'] or 'Clinic'}<br/>{r['doctor_name'] or ''}", normal_style),
                Paragraph(highlights, normal_style)
            ])
        rep_table = Table(rep_rows, colWidths=[70, 150, 150, 170])
        rep_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0F2FE')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(rep_table)
    else:
        story.append(Paragraph("No diagnostic reports logged during this calendar month.", normal_style))
    story.append(Spacer(1, 10))

    # 4. Appointments
    story.append(Paragraph("4. Medical Appointments", heading_style))
    if appointments:
        app_rows = [[
            Paragraph("<b>Date & Time</b>", bold_style),
            Paragraph("<b>Doctor & Facility</b>", bold_style),
            Paragraph("<b>Mode</b>", bold_style),
            Paragraph("<b>Status</b>", bold_style)
        ]]
        for a in appointments:
            app_rows.append([
                Paragraph(f"{a['appointment_date']} {a['appointment_time']}", normal_style),
                Paragraph(f"{a['doctor_name']}<br/>{a['facility']}", normal_style),
                Paragraph(a["mode"], normal_style),
                Paragraph(a["status"].capitalize(), normal_style)
            ])
        app_table = Table(app_rows, colWidths=[120, 200, 100, 120])
        app_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0F2FE')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(app_table)
    else:
        story.append(Paragraph("No appointments recorded for this period.", normal_style))
    story.append(Spacer(1, 15))

    # Disclaimer Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#9CA3AF'), spaceAfter=6))
    story.append(Paragraph(PDF_DISCLAIMER, disclaimer_style))

    # Build the document
    doc.build(story)

    # Save reference in monthly_summaries table
    execute_insert("""
        INSERT INTO monthly_summaries (user_id, month_year, summary_pdf_path)
        VALUES (?, ?, ?)
    """, (user_id, month_year, str(pdf_path)))

    log_audit(
        actor_id=current_user["id"],
        target_id=user_id,
        action="MONTHLY_SUMMARY_PDF_GENERATED",
        resource_type="monthly_summaries",
        resource_id=f"{user_id}:{month_year}"
    )

    return str(pdf_path)
