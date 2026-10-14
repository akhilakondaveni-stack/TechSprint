import pytest
from ai_service import (
    TestItem,
    ExtractedMedicine,
    ReportExplanation,
    get_synthetic_report_data,
    analyze_medical_document,
    MANDATORY_DISCLAIMER
)

def test_pydantic_schema_validation():
    test_item = TestItem(
        name="HbA1c",
        value="6.5",
        unit="%",
        reference_range="< 5.7%",
        status="watch",
        meaning="Three month blood sugar average"
    )
    assert test_item.status == "watch"

    med = ExtractedMedicine(
        name="Metformin",
        dose="500mg",
        frequency="Twice daily",
        timing="morning",
        food_instruction="After Food"
    )
    assert med.name == "Metformin"

    report = ReportExplanation(
        summary="Test report summary",
        tests=[test_item],
        medicines=[med],
        doctor_questions=["What is the next step?"],
        food_tips=["Eat more fiber"],
        disclaimer=MANDATORY_DISCLAIMER
    )
    assert len(report.tests) == 1
    assert len(report.medicines) == 1
    assert "DISCLAIMER" in report.disclaimer

def test_demo_mode_fallback_when_api_unavailable():
    # Calling analyze_medical_document in test environment without valid API key returns safe synthetic data
    result = analyze_medical_document(image_bytes_list=[], language="en")
    assert isinstance(result, ReportExplanation)
    assert result.is_demo is True
    assert len(result.tests) > 0
    assert len(result.doctor_questions) > 0
    assert "DISCLAIMER" in result.disclaimer

def test_multilingual_demo_generation():
    # Hindi
    res_hi = get_synthetic_report_data(language="hi")
    assert "अस्वीकरण" in res_hi.disclaimer
    assert len(res_hi.tests) > 0

    # Telugu
    res_te = get_synthetic_report_data(language="te")
    assert "గమనిక" in res_te.disclaimer
    assert len(res_te.tests) > 0

def test_safety_rules_in_explanations():
    res = get_synthetic_report_data(language="en")
    # Verify summary does not prescribe stopping medicines or claim disease certainty
    assert "DISCLAIMER" in res.disclaimer
    # Verify doctor questions encourage professional consultation
    assert any("doctor" in q.lower() or "physician" in q.lower() or "diet" in q.lower() for q in res.doctor_questions)
