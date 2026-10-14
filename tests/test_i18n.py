import pytest
import config
from i18n import t, generate_tts_audio, TRANSLATIONS
from app import CUSTOM_CSS

def test_translation_keys_exist_for_all_supported_languages():
    languages = ["en", "hi", "te"]
    for key, trans_dict in TRANSLATIONS.items():
        for lang in languages:
            assert lang in trans_dict, f"Missing translation for key '{key}' in language '{lang}'"
            assert len(trans_dict[lang]) > 0

def test_bilingual_supported_languages_config():
    """Requirement 1: Language selector must have English 🇬🇧 and తెలుగు 🇮🇳"""
    assert "en" in config.SUPPORTED_LANGUAGES
    assert "te" in config.SUPPORTED_LANGUAGES
    assert "English 🇬🇧" in config.SUPPORTED_LANGUAGES["en"]
    assert "తెలుగు 🇮🇳" in config.SUPPORTED_LANGUAGES["te"]

def test_telugu_characters_present_in_translations():
    """Requirement 8: Telugu translations should contain genuine Telugu unicode characters"""
    telugu_found = False
    for key, trans_dict in TRANSLATIONS.items():
        te_text = trans_dict.get("te", "")
        # Unicode range for Telugu is \u0C00 - \u0C7F
        for char in te_text:
            if '\u0C00' <= char <= '\u0C7F':
                telugu_found = True
                break
        if telugu_found:
            break
    assert telugu_found, "No Telugu Unicode characters detected in translations dictionary"

def test_telugu_font_in_custom_css():
    """Requirement 8: Ensure a suitable Telugu-supported font is loaded in CSS"""
    assert "Noto Sans Telugu" in CUSTOM_CSS

def test_kwargs_formatting_in_t():
    """Verify string interpolation with kwargs works in t()"""
    en_score = t("health_score_adherence", "en", score=90)
    assert "90%" in en_score
    te_score = t("health_score_adherence", "te", score=90)
    assert "90%" in te_score

def test_all_pages_have_comprehensive_keys():
    """Requirement 2, 4 & 5: Centralized translation covers all major views"""
    critical_keys = [
        # Navbar & Dock
        "app_title", "nav_dashboard", "nav_reports", "nav_medicines", "nav_ask", "nav_more",
        # Auth View
        "auth_welcome_title", "tab_login", "tab_register", "tab_demo", "login_button", "register_button",
        # Dashboard
        "dashboard_greeting", "health_score_title", "still_to_take_today", "card_reports_short",
        # Report reader
        "reader_title", "tab_upload_file", "tab_camera", "btn_analyze", "btn_save_report",
        # Medicine manager
        "med_mgr_title", "tab_med_sched", "tab_dose_log", "tab_analytics", "btn_add_med_submit",
        # Appointment manager
        "app_mgr_title", "tab_app_list", "tab_app_new", "btn_schedule_submit",
        # History & PDF
        "hist_title", "tab_hist_archive", "tab_hist_pdf", "btn_generate_pdf",
        # Family connections
        "fam_title", "fam_parent_portal", "fam_child_portal", "btn_gen_invite",
        # Settings
        "settings_title", "tab_set_profile", "tab_set_telegram", "tab_set_privacy", "btn_save_profile",
        # Footer
        "footer_rights", "footer_disclaimer"
    ]
    for k in critical_keys:
        assert k in TRANSLATIONS, f"Critical key '{k}' missing from TRANSLATIONS"
        assert "en" in TRANSLATIONS[k]
        assert "te" in TRANSLATIONS[k]
        assert len(TRANSLATIONS[k]["en"]) > 0
        assert len(TRANSLATIONS[k]["te"]) > 0

def test_t_function_fallback():
    assert t("non_existent_key", "en") == "non_existent_key"
    assert "HealthBuddy" in t("app_title", "en")
    assert "హెల్త్‌బడ్డీ" in t("app_title", "te")

def test_tts_graceful_handling_empty():
    assert generate_tts_audio("") is None
    assert generate_tts_audio(None) is None
