import io
import logging
from typing import Dict, Any, Optional
from gtts import gTTS

logger = logging.getLogger(__name__)

# UI Translations Dictionary (Bilingual EN/TE with HI fallback)
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # App & Navbar
    "app_title": {
        "en": "HealthBuddy for Parents",
        "te": "హెల్త్‌బడ్డీ (తల్లిదండ్రుల కొరకు)",
        "hi": "हेल्थबडी (माता-पिता के लिए)"
    },
    "app_tagline": {
        "en": "Compassionate, secure AI healthcare assistant for elderly parents and family.",
        "te": "వృద్ధులైన తల్లిదండ్రులు మరియు కుటుంబ సభ్యుల కోసం సురక్షిత AI ఆరోగ్య సహాయకుడు.",
        "hi": "बुजुर्ग माता-पिता और परिवार के लिए सुरक्षित AI स्वास्थ्य सहायक।"
    },
    "nav_dashboard": {
        "en": "Dashboard",
        "te": "డ్యాష్‌బోర్డ్",
        "hi": "डैशबोर्ड"
    },
    "nav_reports": {
        "en": "Reports",
        "te": "రిపోర్టులు",
        "hi": "रिपोर्ट्स"
    },
    "nav_medicines": {
        "en": "Medicines",
        "te": "మందులు",
        "hi": "दवाएं"
    },
    "nav_ask": {
        "en": "Ask AI",
        "te": "AI ని అడగండి",
        "hi": "AI से पूछें"
    },
    "nav_more": {
        "en": "More",
        "te": "మరిన్ని",
        "hi": "और अधिक"
    },
    "nav_dock_label": {
        "en": "Navigation Dock",
        "te": "నావిగేషన్ డాక్",
        "hi": "नेविगेशन डॉक"
    },
    "nav_report_reader": {
        "en": "Medical Report Reader",
        "te": "మెడికల్ రిపోర్ట్ రీడర్",
        "hi": "मेडिकल रिपोर्ट रीडर"
    },
    "nav_medicine_manager": {
        "en": "Medicine Manager",
        "te": "మందుల నిర్వహణ",
        "hi": "दवा प्रबंधक"
    },
    "nav_appointment_manager": {
        "en": "Appointment Manager",
        "te": "అపాయింట్‌మెంట్స్",
        "hi": "अपॉइंटमेंट प्रबंधक"
    },
    "nav_health_history": {
        "en": "Health History",
        "te": "ఆరోగ్య చరిత్ర",
        "hi": "स्वास्थ्य इतिहास"
    },
    "nav_family": {
        "en": "Family Connections",
        "te": "కుటుంబ బంధాలు",
        "hi": "पारिवारिक संबंध"
    },
    "nav_settings": {
        "en": "Settings",
        "te": "సెట్టింగ్‌లు",
        "hi": "सेटिंग्स"
    },
    "logout": {
        "en": "Log Out",
        "te": "లాగ్ అవుట్",
        "hi": "लॉग आउट"
    },
    "logout_btn": {
        "en": "🚪 Log Out of HealthBuddy",
        "te": "🚪 హెల్త్‌బడ్డీ నుండి లాగ్ అవుట్ అవ్వండి",
        "hi": "🚪 हेल्थबडी से लॉग आउट करें"
    },
    "logged_in_as": {
        "en": "Logged in as",
        "te": "లాగిన్ అయ్యారు",
        "hi": "के रूप में लॉग इन"
    },
    "role_parent": {
        "en": "Parent",
        "te": "తల్లిదండ్రులు",
        "hi": "माता-पिता"
    },
    "role_child": {
        "en": "Child / Family Member",
        "te": "కుటుంబ సభ్యులు / సంరక్షకుడు",
        "hi": "बच्चा / परिवार का सदस्य"
    },
    "parent_switcher_label": {
        "en": "Parent",
        "te": "తల్లిదండ్రులు",
        "hi": "माता-पिता"
    },
    "lang_selector_label": {
        "en": "Language",
        "te": "భాష",
        "hi": "भाषा"
    },

    # Auth View (Login / Register / Quick Demo)
    "auth_welcome_title": {
        "en": "🌿 HealthBuddy for Parents",
        "te": "🌿 తల్లిదండ్రుల కొరకు హెల్త్‌బడ్డీ",
        "hi": "🌿 हेल्थबडी (माता-पिता के लिए)"
    },
    "auth_welcome_desc": {
        "en": "A compassionate, secure AI healthcare assistant designed for elderly parents and family caregivers. Understand medical reports, manage daily medicines, and keep loved ones connected.",
        "te": "వృద్ధులైన తల్లిదండ్రులు మరియు కుటుంబ సంరక్షకుల కోసం రూపొందించిన సురక్షితమైన AI ఆరోగ్య సహాయకుడు. వైద్య నివేదికలను సులభంగా అర్థం చేసుకోండి, రోజువారీ మందులను సమయానికి తీసుకోండి, కుటుంబ సభ్యులతో కనెక్ట్ అయి ఉండండి.",
        "hi": "बुजुर्ग माता-पिता और देखभाल करने वालों के लिए बनाया गया सुरक्षित AI स्वास्थ्य सहायक।"
    },
    "tab_login": {
        "en": "🔐 Log In",
        "te": "🔐 లాగిన్",
        "hi": "🔐 लॉग इन"
    },
    "tab_register": {
        "en": "📝 Create Account",
        "te": "📝 కొత్త ఖాతా",
        "hi": "📝 खाता बनाएं"
    },
    "tab_demo": {
        "en": "⚡ Quick Demo Login",
        "te": "⚡ తక్షణ డెమో",
        "hi": "⚡ त्वरित डेमो"
    },
    "login_heading": {
        "en": "Welcome Back",
        "te": "తిరిగి స్వాగతం",
        "hi": "वापसी पर स्वागत है"
    },
    "email_label": {
        "en": "Email Address",
        "te": "ఈమెయిల్ చిరునామా",
        "hi": "ईमेल पता"
    },
    "password_label": {
        "en": "Password",
        "te": "పాస్‌వర్డ్",
        "hi": "पासवर्ड"
    },
    "password_placeholder": {
        "en": "Enter your password",
        "te": "మీ పాస్‌వర్డ్ నమోదు చేయండి",
        "hi": "अपना पासवर्ड दर्ज करें"
    },
    "login_button": {
        "en": "Log In to HealthBuddy",
        "te": "హెల్త్‌బడ్డీలోకి లాగిన్ అవ్వండి",
        "hi": "हेल्थबडी में लॉग इन करें"
    },
    "err_enter_email_pass": {
        "en": "Please enter both email and password.",
        "te": "దయచేసి ఈమెయిల్ మరియు పాస్‌వర్డ్ రెండింటినీ నమోదు చేయండి.",
        "hi": "कृपया ईमेल और पासवर्ड दोनों दर्ज करें।"
    },
    "register_heading": {
        "en": "Create a New Account",
        "te": "కొత్త ఖాతాను సృష్టించండి",
        "hi": "नया खाता बनाएं"
    },
    "full_name_label": {
        "en": "Full Name",
        "te": "పూర్తి పేరు",
        "hi": "पूरा नाम"
    },
    "full_name_placeholder": {
        "en": "e.g. Ramachandra Rao",
        "te": "ఉదా. రామచంద్రరావు",
        "hi": "उदा. रामचंद्र राव"
    },
    "password_help": {
        "en": "Must be at least 8 characters long",
        "te": "కనీసం 8 అక్షరాలు ఉండాలి",
        "hi": "कम से कम 8 अक्षर होने चाहिए"
    },
    "role_label": {
        "en": "Your Role",
        "te": "మీ పాత్ర",
        "hi": "आपकी भूमिका"
    },
    "role_parent_option": {
        "en": "👴 Parent (Managing personal health)",
        "te": "👴 తల్లిదండ్రులు (వ్యక్తిగత ఆరోగ్యాన్ని పర్యవేక్షించడం)",
        "hi": "👴 माता-पिता (व्यक्तिगत स्वास्थ्य प्रबंधन)"
    },
    "role_child_option": {
        "en": "👨‍👩‍👧 Child / Family Member (Caregiver)",
        "te": "👨‍👩‍👧 కుమారుడు / కుటుంబ సభ్యులు (సంరక్షకుడు)",
        "hi": "👨‍👩‍👧 बच्चा / परिवार का सदस्य (देखभालकर्ता)"
    },
    "phone_label": {
        "en": "Phone Number (Optional)",
        "te": "ఫోన్ నంబర్ (ఐచ్ఛికం)",
        "hi": "फ़ोन नंबर (वैकल्पिक)"
    },
    "preferred_lang_label": {
        "en": "Preferred Language",
        "te": "ప్రాధాన్య భాష",
        "hi": "पसंदीदा भाषा"
    },
    "register_button": {
        "en": "Register Account",
        "te": "ఖాతాను నమోదు చేయండి",
        "hi": "खाता पंजीकृत करें"
    },
    "demo_heading": {
        "en": "Instant Demo Access",
        "te": "తక్షణ డెమో యాక్సెస్",
        "hi": "त्वरित डेमो पहुंच"
    },
    "demo_info": {
        "en": "Pre-seeded test accounts for instant exploration of parent & child workflows:",
        "te": "తల్లిదండ్రులు మరియు కుటుంబ సభ్యుల ఫీచర్లను సులభంగా పరీక్షించడానికి సిద్ధంగా ఉన్న ఖాతాలు:",
        "hi": "परीक्षण खाते उपलब्ध हैं:"
    },
    "demo_parent_btn": {
        "en": "👴 Log in as Parent (Ramachandra Rao)",
        "te": "👴 తల్లిదండ్రులుగా లాగిన్ అవ్వండి (రామచంద్రరావు)",
        "hi": "👴 माता-पिता के रूप में लॉग इन करें (रामचंद्र राव)"
    },
    "demo_child_btn": {
        "en": "👧 Log in as Child (Kavita Rao)",
        "te": "👧 కుటుంబ సభ్యురాలిగా లాగిన్ అవ్వండి (కవితా రావు)",
        "hi": "👧 बच्चे के रूप में लॉग इन करें (कविता राव)"
    },
    "demo_creds_caption": {
        "en": "Default credentials: parent@healthbuddy.com / Password123! | child@healthbuddy.com / Password123!",
        "te": "డిఫాల్ట్ వివరాలు: parent@healthbuddy.com / Password123! | child@healthbuddy.com / Password123!",
        "hi": "डिफ़ॉल्ट क्रेडेंशियल्स: parent@healthbuddy.com / Password123!"
    },

    # Dashboard
    "dashboard_connect_parent_warning": {
        "en": "Please connect to a parent account to view their dashboard.",
        "te": "డ్యాష్‌బోర్డ్‌ను చూడటానికి దయచేసి తల్లిదండ్రుల ఖాతాకు కనెక్ట్ అవ్వండి.",
        "hi": "डैशबोर्ड देखने के लिए कृपया माता-पिता के खाते से जुड़ें।"
    },
    "dashboard_access_denied": {
        "en": "Access denied: You do not have permission to view this parent's health record.",
        "te": "యాక్సెస్ నిరాకరించబడింది: ఈ తల్లిదండ్రుల ఆరోగ్య రికార్డును చూసే అనుమతి మీకు లేదు.",
        "hi": "पहुंच अस्वीकृत: अनुमति नहीं है।"
    },
    "dashboard_greeting": {
        "en": "Hello 👋",
        "te": "నమస్కారం 👋",
        "hi": "नमस्ते 👋"
    },
    "health_score_title": {
        "en": "Health score",
        "te": "ఆరోగ్య స్కోర్",
        "hi": "स्वास्थ्य स्कोर"
    },
    "health_score_adherence": {
        "en": "Medicine adherence {score}% this month",
        "te": "ఈ నెల మందుల క్రమం {score}%",
        "hi": "इस महीने दवा अनुपालन {score}%"
    },
    "health_score_desc": {
        "en": "A simple guide made from your own reports and medicine log. Not a medical score. Informational only, not a diagnosis. Please consult a doctor.",
        "te": "మీ నివేదికలు మరియు మందుల వివరాల ఆధారంగా రూపొందించిన సాధారణ సూచిక. ఇది వైద్య స్కోర్ కాదు. కేవలం సమాచారం కొరకు మాత్రమే, రోగనిర్ధారణ కాదు. దయచేసి వైద్యుడిని సంప్రదించండి.",
        "hi": "यह आपके रिकॉर्ड के आधार पर एक सरल मार्गदर्शिका है।"
    },
    "card_reports": {
        "en": "Total Medical Reports",
        "te": "మొత్తం వైద్య నివేదికలు",
        "hi": "कुल मेडिकल रिपोर्ट्स"
    },
    "card_reports_short": {
        "en": "Reports",
        "te": "రిపోర్టులు",
        "hi": "रिपोर्ट्स"
    },
    "card_medicines": {
        "en": "Active Medicines",
        "te": "ప్రస్తుత మందులు",
        "hi": "सक्रिय दवाएं"
    },
    "card_medicines_short": {
        "en": "Medicines",
        "te": "మందులు",
        "hi": "दवाएं"
    },
    "card_adherence": {
        "en": "Today's Adherence",
        "te": "ఈ రోజు మందుల క్రమం",
        "hi": "आज की दवा अनुपालन"
    },
    "card_appointments": {
        "en": "Upcoming Appointments",
        "te": "రాబోయే అపాయింట్‌మెంట్‌లు",
        "hi": "आगामी अपॉइंटमेंट्स"
    },
    "card_appointments_short": {
        "en": "Appointments",
        "te": "అపాయింట్‌మెంట్‌లు",
        "hi": "अपॉइंटमेंट्स"
    },
    "still_to_take_today": {
        "en": "Still to take today",
        "te": "ఈ రోజు ఇంకా వేసుకోవాల్సిన మందులు",
        "hi": "आज अभी लेना बाकी है"
    },
    "nothing_pending": {
        "en": "Nothing pending 🎉",
        "te": "అన్నీ పూర్తయ్యాయి 🎉",
        "hi": "कुछ भी लंबित नहीं 🎉"
    },
    "btn_taken": {
        "en": "Taken",
        "te": "తీసుకున్నాను",
        "hi": "ले ली"
    },
    "btn_skip": {
        "en": "Skip",
        "te": "దాటవేయి",
        "hi": "छोड़ें"
    },
    "btn_skipped": {
        "en": "Skipped",
        "te": "విడిచిపెట్టాను",
        "hi": "छोड़ी"
    },
    "btn_missed": {
        "en": "Missed",
        "te": "మర్చిపోయాను",
        "hi": "छूट गई"
    },
    "cta_report_text": {
        "en": "👉 Start by reading your first report: take a photo of a lab report or prescription.",
        "te": "👉 మీ మొదటి వైద్య నివేదికను పరిశీలించండి: ల్యాబ్ రిపోర్ట్ లేదా ప్రిస్క్రిప్షన్ ఫోటో తీయండి.",
        "hi": "👉 अपनी पहली रिपोर्ट पढ़ें: लैब रिपोर्ट या प्रिस्क्रिप्शन की फोटो लें।"
    },
    "cta_upload_btn": {
        "en": "Upload",
        "te": "అప్‌లోడ్",
        "hi": "अपलोड"
    },
    "today_medicine_tracker": {
        "en": "💊 Today's Medicine Tracker",
        "te": "💊 ఈ రోజు మందుల ట్రాకర్",
        "hi": "💊 आज का दवा ट्रैकर"
    },
    "no_scheduled_meds": {
        "en": "No scheduled medications for today. Add medications in the Medicine Manager tab.",
        "te": "ఈ రోజుకు ఎటువంటి మందులు షెడ్యూల్ చేయబడలేదు. మందుల నిర్వహణ ట్యాబ్‌లో జోడించండి.",
        "hi": "आज के लिए कोई दवा निर्धारित नहीं है।"
    },
    "trends_title": {
        "en": "📈 Health Parameter Trends (Biomarkers Over Time)",
        "te": "📈 ఆరోగ్య పారామితుల పోకడలు (కాలక్రమేణా మార్పులు)",
        "hi": "📈 स्वास्थ्य पैरामीटर रुझान"
    },
    "trends_caption": {
        "en": "Historical values compared across verified reports. *Visual trend only — consult your doctor.*",
        "te": "ధృవీకరించబడిన నివేదికలలోని మార్పులు. *కేవలం దృశ్య అవగాహన కొరకు మాత్రమే — వైద్యుడిని సంప్రదించండి.*",
        "hi": "सत्यापित रिपोर्टों में तुलना। केवल दृश्य रुझान।"
    },
    "select_test_trend": {
        "en": "Select Test to Visualize Trend",
        "te": "పోకడను చూడటానికి పరీక్షను ఎంచుకోండి",
        "hi": "रुझान देखने के लिए परीक्षण चुनें"
    },
    "insufficient_trend_data": {
        "en": "Insufficient data points for this test.",
        "te": "ఈ పరీక్ష కోసం తగినన్ని డేటా పాయింట్లు లేవు.",
        "hi": "अपर्याप्त डेटा।"
    },
    "no_lab_tests_trend": {
        "en": "No numerical lab tests recorded yet. Upload a report in the Medical Report Reader to populate trends.",
        "te": "ఇంకా ల్యాబ్ పరీక్షలు నమోదు కాలేదు. వివరాలను చూడటానికి మెడికల్ రిపోర్ట్ రీడర్‌లో నివేదికను అప్‌లోడ్ చేయండి.",
        "hi": "कोई लैब परीक्षण दर्ज नहीं।"
    },

    # Time Slots & Dose Statuses
    "morning": {
        "en": "Morning (08:00)",
        "te": "ఉదయం (08:00)",
        "hi": "सुबह (08:00)"
    },
    "afternoon": {
        "en": "Afternoon (14:00)",
        "te": "మధ్యాహ్నం (14:00)",
        "hi": "दोपहर (14:00)"
    },
    "night": {
        "en": "Night (20:00)",
        "te": "రాత్రి (20:00)",
        "hi": "रात (20:00)"
    },
    "mark_taken": {
        "en": "✅ Taken",
        "te": "✅ తీసుకున్నాను",
        "hi": "✅ ले ली"
    },
    "mark_skipped": {
        "en": "⏭️ Skipped",
        "te": "⏭️ విడిచిపెట్టాను",
        "hi": "⏭️ छोड़ी"
    },
    "mark_missed": {
        "en": "❌ Missed",
        "te": "❌ మర్చిపోయాను",
        "hi": "❌ छूट गई"
    },

    # More Hub
    "more_hub_title": {
        "en": "☰ More Health Services",
        "te": "☰ మరిన్ని ఆరోగ్య సేవలు",
        "hi": "☰ अन्य स्वास्थ्य सेवाएं"
    },
    "more_hub_caption": {
        "en": "Access appointments, official monthly summary PDFs, family connections, and settings.",
        "te": "అపాయింట్‌మెంట్‌లు, నెలవారీ సారాంశ PDFలు, కుటుంబ బంధాలు మరియు సెట్టింగ్‌లను నిర్వహించండి.",
        "hi": "अपॉइंटमेंट्स, मासिक सारांश PDF, परिवार और सेटिंग्स।"
    },
    "hub_app_title": {
        "en": "🗓️ Appointment Manager",
        "te": "🗓️ అపాయింట్‌మెంట్స్ నిర్వహణ",
        "hi": "🗓️ अपॉइंटमेंट प्रबंधक"
    },
    "hub_app_desc": {
        "en": "Schedule doctor consultations, track upcoming visits, and view past checkups.",
        "te": "వైద్యుల సంప్రదింపులను షెడ్యూల్ చేయండి, రాబోయే మరియు గత సందర్శనలను ట్రాక్ చేయండి.",
        "hi": "डॉक्टर की सलाह निर्धारित करें।"
    },
    "hub_app_btn": {
        "en": "Open Appointments",
        "te": "అపాయింట్‌మెంట్స్ తెరవండి",
        "hi": "अपॉइंटमेंट्स खोलें"
    },
    "hub_fam_title": {
        "en": "👨‍👩‍👧 Family Connections",
        "te": "👨‍👩‍👧 కుటుంబ బంధాలు",
        "hi": "👨‍👩‍👧 पारिवारिक संबंध"
    },
    "hub_fam_desc": {
        "en": "Manage family invitation codes, approve caregiver access, and review sharing permissions.",
        "te": "కుటుంబ ఆహ్వాన కోడ్‌లను నిర్వహించండి, సంరక్షకుల యాక్సెస్‌ను ఆమోదించండి మరియు అనుమతులను సమీక్షించండి.",
        "hi": "परिवार आमंत्रण प्रबंधित करें।"
    },
    "hub_fam_btn": {
        "en": "Open Family Connections",
        "te": "కుటుంబ బంధాలు తెరవండి",
        "hi": "परिवार खोलें"
    },
    "hub_hist_title": {
        "en": "📜 Health History & PDF Export",
        "te": "📜 ఆరోగ్య చరిత్ర & PDF డౌన్‌లోడ్",
        "hi": "📜 स्वास्थ्य इतिहास और PDF"
    },
    "hub_hist_desc": {
        "en": "Search archived reports and download official monthly summary PDFs for your physician.",
        "te": "గత నివేదికలను శోధించండి మరియు మీ వైద్యుని కోసం అధికారిక నెలవారీ PDF సారాంశాన్ని డౌన్‌లోడ్ చేయండి.",
        "hi": "रिपोर्ट खोजें और PDF डाउनलोड करें।"
    },
    "hub_hist_btn": {
        "en": "Open Health History",
        "te": "ఆరోగ్య చరిత్రను తెరవండి",
        "hi": "स्वास्थ्य इतिहास खोलें"
    },
    "hub_set_title": {
        "en": "⚙️ Profile & System Settings",
        "te": "⚙️ ప్రొఫైల్ & సిస్టమ్ సెట్టింగ్‌లు",
        "hi": "⚙️ प्रोफ़ाइल और सिस्टम सेटिंग्स"
    },
    "hub_set_desc": {
        "en": "Configure Telegram notifications, language preferences, and review privacy architecture.",
        "te": "టెలిగ్రామ్ నోటిఫికేషన్‌లు, భాషా ప్రాధాన్యతలను కాన్ఫిగర్ చేయండి మరియు భద్రతా విధానాలను సమీక్షించండి.",
        "hi": "टेलीग्राम सूचनाएं और सेटिंग्स।"
    },
    "hub_set_btn": {
        "en": "Open Settings",
        "te": "సెట్టింగ్‌లు తెరవండి",
        "hi": "सेटिंग्स खोलें"
    },

    # Report Reader
    "reader_title": {
        "en": "📄 Medical Report Reader & AI Explainer",
        "te": "📄 మెడికల్ రిపోర్ట్ రీడర్ & AI వివరణ",
        "hi": "📄 मेडिकल रिपोर्ट रीडर और AI"
    },
    "reader_caption": {
        "en": "Upload lab tests, doctor prescriptions, or discharge summaries. Claude AI extracts values and explains them in clear, compassionate language.",
        "te": "ల్యాబ్ పరీక్షలు, ప్రిస్క్రిప్షన్‌లు లేదా డిశ్చార్జ్ సారాంశాలను అప్‌లోడ్ చేయండి. AI కీలక విలువలను సేకరించి సులభమైన భాషలో వివరిస్తుంది.",
        "hi": "रिपोर्ट अपलोड करें और समझें।"
    },
    "tab_upload_file": {
        "en": "📁 Upload File (PDF / Image)",
        "te": "📁 ఫైల్ అప్‌లోడ్ (PDF / చిత్రం)",
        "hi": "📁 फ़ाइल अपलोड (PDF / छवि)"
    },
    "tab_camera": {
        "en": "📸 Camera Capture",
        "te": "📸 కెమెరా ద్వారా తీయండి",
        "hi": "📸 कैमरा कैप्चर"
    },
    "uploader_label": {
        "en": "Choose a medical report file (PDF, PNG, JPG, JPEG - Max 10MB, up to 5 pages)",
        "te": "వైద్య నివేదిక ఫైల్‌ను ఎంచుకోండి (PDF, PNG, JPG, JPEG - గరిష్టంగా 10MB, 5 పేజీల వరకు)",
        "hi": "मेडिकल रिपोर्ट फ़ाइल चुनें"
    },
    "camera_label": {
        "en": "Capture report document using camera",
        "te": "కెమెరా ఉపయోగించి రిపోర్ట్ ఫోటో తీయండి",
        "hi": "कैमरे से फोटो लें"
    },
    "difficulty_label": {
        "en": "Explanation Detail Level",
        "te": "వివరణ స్థాయి",
        "hi": "विवरण स्तर"
    },
    "diff_simple": {
        "en": "Simple",
        "te": "సులభమైన శైలి",
        "hi": "सरल"
    },
    "diff_detailed": {
        "en": "Detailed",
        "te": "సవివరమైన శైలి",
        "hi": "विस्तृत"
    },
    "difficulty_help": {
        "en": "Simple gives gentle, everyday language. Detailed includes clinical reference ranges.",
        "te": "సులభమైన శైలి తేలికపాటి పదాలతో వివరిస్తుంది. సవివరమైన శైలి వైద్య ప్రమాణాలను చూపుతుంది.",
        "hi": "सरल या विस्तृत स्तर।"
    },
    "category_label": {
        "en": "Report Category",
        "te": "నివేదిక వర్గం",
        "hi": "रिपोर्ट श्रेणी"
    },
    "cat_lab": {
        "en": "Lab Report",
        "te": "ల్యాబ్ రిపోర్ట్",
        "hi": "लैब रिपोर्ट"
    },
    "cat_rx": {
        "en": "Prescription",
        "te": "ప్రిస్క్రిప్షన్",
        "hi": "प्रिस्क्रिप्शन"
    },
    "cat_discharge": {
        "en": "Discharge Summary",
        "te": "డిశ్చార్జ్ సారాంశం",
        "hi": "डिस्चार्ज सारांश"
    },
    "cat_consult": {
        "en": "Doctor Consultation Note",
        "te": "డాక్టర్ కన్సల్టేషన్ నోట్",
        "hi": "परामर्श नोट"
    },
    "btn_analyze": {
        "en": "🔍 Analyze Document with HealthBuddy AI",
        "te": "🔍 హెల్త్‌బడ్డీ AI తో నివేదికను విశ్లేషించండి",
        "hi": "🔍 AI के साथ विश्लेषण करें"
    },
    "spinner_analyzing": {
        "en": "Carefully analyzing document values, medications, and generating safe explanation...",
        "te": "నివేదిక వివరాలను, మందులను విశ్లేషించి సురక్షితమైన వివరణను సిద్ధం చేస్తోంది...",
        "hi": "दस्तावेज़ का विश्लेषण हो रहा है..."
    },
    "preview_expander": {
        "en": "👁️ View Uploaded Document Preview",
        "te": "👁️ అప్‌లోడ్ చేసిన డాక్యుమెంట్ ప్రివ్యూ చూడండి",
        "hi": "👁️ पूर्वावलोकन देखें"
    },
    "page_caption": {
        "en": "Page",
        "te": "పేజీ",
        "hi": "पृष्ठ"
    },
    "review_title": {
        "en": "📋 Review & Edit Extracted Medical Information",
        "te": "📋 సేకరించిన వైద్య సమాచారాన్ని సమీక్షించండి & సవరించండి",
        "hi": "📋 जानकारी की समीक्षा करें"
    },
    "review_caption": {
        "en": "You have full control. Review and correct any extracted test values before saving to your permanent health history.",
        "te": "పూర్తి నియంత్రణ మీ చేతుల్లోనే ఉంది. శాశ్వత ఆరోగ్య చరిత్రలో సేవ్ చేయడానికి ముందు పరీక్ష విలువలను సరిచూసుకోండి.",
        "hi": "सहेजने से पहले जांच लें।"
    },
    "demo_mode_badge": {
        "en": "⚠️ Demo Mode Active (Synthetic Analysis)",
        "te": "⚠️ డెమో మోడ్ సక్రియంగా ఉంది (నమూనా విశ్లేషణ)",
        "hi": "⚠️ डेमो मोड सक्रिय (सिंथेटिक विश्लेषण)"
    },
    "summary_heading": {
        "en": "🗣️ Compassionate AI Summary",
        "te": "🗣️ AI అందించిన ఆరోగ్య సారాంశం",
        "hi": "🗣️ AI सारांश"
    },
    "listen_audio": {
        "en": "🔊 Listen to Summary (Audio)",
        "te": "🔊 సారాంశం వినండి (ఆడియో)",
        "hi": "🔊 सारांश सुनें (ऑडियो)"
    },
    "audio_spinner": {
        "en": "Generating gentle audio explanation...",
        "te": "ఆడియో వివరణను రూపొందిస్తోంది...",
        "hi": "ऑडियो तैयार हो रहा है..."
    },
    "audio_offline_warning": {
        "en": "Audio playback is unavailable (offline mode). Please read the written summary above.",
        "te": "ఆడియో ప్లేబ్యాక్ అందుబాటులో లేదు (ఆఫ్‌లైన్ మోడ్). దయచేసి పైన ఉన్న లిఖిత సారాంశాన్ని చదవండి.",
        "hi": "ऑडियो उपलब्ध नहीं है।"
    },
    "tests_heading": {
        "en": "🔬 Extracted Diagnostic Tests",
        "te": "🔬 సేకరించిన రోగనిర్ధారణ పరీక్షలు",
        "hi": "🔬 नैदानिक ​​परीक्षण"
    },
    "no_tests_detected": {
        "en": "No specific laboratory tests detected in this document.",
        "te": "ఈ పత్రంలో ల్యాబ్ పరీక్షలేవీ గుర్తించబడలేదు.",
        "hi": "कोई लैब टेस्ट नहीं मिले।"
    },
    "meds_heading": {
        "en": "💊 Extracted Prescription Medicines",
        "te": "💊 సేకరించిన మందుల ప్రిస్క్రిప్షన్",
        "hi": "💊 दवाएं"
    },
    "no_meds_detected": {
        "en": "No prescription medications detected in this document.",
        "te": "ఈ పత్రంలో ప్రిస్క్రిప్షన్ మందులేవీ గుర్తించబడలేదు.",
        "hi": "कोई दवा नहीं मिली।"
    },
    "doctor_questions_heading": {
        "en": "❓ Questions to Ask Your Doctor",
        "te": "❓ మీ వైద్యుడిని అడగవలసిన ప్రశ్నలు",
        "hi": "❓ डॉक्टर से पूछने योग्य प्रश्न"
    },
    "diet_tips_heading": {
        "en": "🥗 Gentle Diet & Lifestyle Information",
        "te": "🥗 ఆహారపు అలవాట్లు & జీవనశైలి సూచనలు",
        "hi": "🥗 आहार और जीवनशैली सुझाव"
    },
    "save_doc_heading": {
        "en": "Save Document",
        "te": "పత్రాన్ని సేవ్ చేయండి",
        "hi": "दस्तावेज़ सहेजें"
    },
    "report_title_label": {
        "en": "Report Title",
        "te": "రిపోర్ట్ శీర్షిక",
        "hi": "रिपोर्ट शीर्षक"
    },
    "report_date_label": {
        "en": "Report Date",
        "te": "రిపోర్ట్ తేదీ",
        "hi": "रिपोर्ट तिथि"
    },
    "doctor_name_label": {
        "en": "Doctor Name",
        "te": "వైద్యుని పేరు",
        "hi": "डॉक्टर का नाम"
    },
    "facility_label": {
        "en": "Hospital or Laboratory",
        "te": "ఆసుపత్రి లేదా ల్యాబ్ పేరు",
        "hi": "अस्पताल या लैब"
    },
    "btn_save_report": {
        "en": "💾 Confirm & Save to Health History",
        "te": "💾 నిర్ధారించండి & ఆరోగ్య చరిత్రలో సేవ్ చేయండి",
        "hi": "💾 पुष्टि करें और सहेजें"
    },
    "report_saved_success": {
        "en": "🎉 Report saved successfully! Added to your permanent medical record.",
        "te": "🎉 నివేదిక విజయవంతంగా సేవ్ చేయబడింది! మీ శాశ్వత వైద్య రికార్డుకు జోడించబడింది.",
        "hi": "🎉 रिपोर्ट सफलतापूर्वक सहेजी गई!"
    },

    # Medicine Manager
    "med_mgr_title": {
        "en": "💊 Medicine Manager & Daily Dose Adherence",
        "te": "💊 మందుల నిర్వహణ & రోజువారీ క్రమశిక్షణ",
        "hi": "💊 दवा प्रबंधक और अनुपालन"
    },
    "med_mgr_caption": {
        "en": "Manage medication schedules, log taken doses, and track adherence trends.",
        "te": "మందుల వేళలను నిర్వహించండి, వేసుకున్న డోసులను నమోదు చేయండి మరియు క్రమాన్ని ట్రాక్ చేయండి.",
        "hi": "दवाएं और अनुपालन ट्रैक करें।"
    },
    "tab_med_sched": {
        "en": "📋 Medication Schedules",
        "te": "📋 మందుల షెడ్యూల్",
        "hi": "📋 दवा अनुसूची"
    },
    "tab_dose_log": {
        "en": "🗓️ Daily Dose Log",
        "te": "🗓️ రోజువారీ డోస్ లాగ్",
        "hi": "🗓️ दैनिक डोज़ लॉग"
    },
    "tab_analytics": {
        "en": "📊 Adherence Analytics",
        "te": "📊 మందుల క్రమ విశ్లేషణ",
        "hi": "📊 अनुपालन विश्लेषण"
    },
    "active_meds_heading": {
        "en": "Active Medications",
        "te": "ప్రస్తుత మందులు",
        "hi": "सक्रिय दवाएं"
    },
    "no_meds_registered": {
        "en": "No medications registered yet. Add a medication schedule below.",
        "te": "ఇంకా మందులేవీ నమోదు చేయలేదు. క్రింద కొత్త మందుల షెడ్యూల్‌ను జోడించండి.",
        "hi": "कोई दवा पंजीकृत नहीं है।"
    },
    "badge_active": {
        "en": "ACTIVE",
        "te": "సక్రియంగా ఉంది",
        "hi": "सक्रिय"
    },
    "badge_inactive": {
        "en": "INACTIVE",
        "te": "నిష్క్రియంగా ఉంది",
        "hi": "निष्क्रिय"
    },
    "label_timing": {
        "en": "Timing",
        "te": "సమయం",
        "hi": "समय"
    },
    "label_food": {
        "en": "Food",
        "te": "ఆహారం",
        "hi": "भोजन"
    },
    "label_duration": {
        "en": "Duration",
        "te": "వ్యవధి",
        "hi": "अवधि"
    },
    "label_ongoing": {
        "en": "Ongoing",
        "te": "కొనసాగుతోంది",
        "hi": "जारी है"
    },
    "btn_deactivate": {
        "en": "Deactivate",
        "te": "నిష్క్రియం చేయి",
        "hi": "निष्क्रिय करें"
    },
    "btn_activate": {
        "en": "Activate",
        "te": "సక్రియం చేయి",
        "hi": "सक्रिय करें"
    },
    "btn_delete": {
        "en": "🗑️ Delete",
        "te": "🗑️ తొలగించు",
        "hi": "🗑️ हटाएं"
    },
    "add_med_heading": {
        "en": "➕ Add New Medication Schedule",
        "te": "➕ కొత్త మందుల షెడ్యూల్‌ను జోడించండి",
        "hi": "➕ नई दवा अनुसूची जोड़ें"
    },
    "med_name_label": {
        "en": "Medicine Name",
        "te": "మందు పేరు",
        "hi": "दवा का नाम"
    },
    "med_dose_label": {
        "en": "Dose / Strength",
        "te": "మోతాదు / బలం",
        "hi": "खुराक / ताकत"
    },
    "freq_label": {
        "en": "Frequency",
        "te": "ఫ్రీక్వెన్సీ (తీసుకోవలసిన సార్లు)",
        "hi": "आवृत्ति"
    },
    "timing_slots_label": {
        "en": "Timing Slots",
        "te": "సమయాలు",
        "hi": "समय स्लॉट"
    },
    "slot_morning_ist": {
        "en": "Morning (08:00 IST)",
        "te": "ఉదయం (08:00 IST)",
        "hi": "सुबह (08:00 IST)"
    },
    "slot_afternoon_ist": {
        "en": "Afternoon (14:00 IST)",
        "te": "మధ్యాహ్నం (14:00 IST)",
        "hi": "दोपहर (14:00 IST)"
    },
    "slot_night_ist": {
        "en": "Night (20:00 IST)",
        "te": "రాత్రి (20:00 IST)",
        "hi": "रात (20:00 IST)"
    },
    "food_instructions_label": {
        "en": "Food Instructions",
        "te": "ఆహార సూచనలు",
        "hi": "भोजन निर्देश"
    },
    "food_after": {
        "en": "After Food",
        "te": "భోజనం తర్వాత",
        "hi": "भोजन के बाद"
    },
    "food_before": {
        "en": "Before Food",
        "te": "భోజనానికి ముందు",
        "hi": "भोजन से पहले"
    },
    "food_with": {
        "en": "With Food",
        "te": "భోజనంతో పాటు",
        "hi": "भोजन के साथ"
    },
    "food_empty": {
        "en": "Empty Stomach",
        "te": "ఖాళీ కడుపుతో",
        "hi": "खाली पेट"
    },
    "duration_label": {
        "en": "Duration",
        "te": "వ్యవధి",
        "hi": "अवधि"
    },
    "btn_add_med_submit": {
        "en": "Add Medication Schedule",
        "te": "మందుల షెడ్యూల్‌ను జోడించండి",
        "hi": "दवा अनुसूची जोड़ें"
    },
    "err_enter_med_dose": {
        "en": "Please enter medicine name and dose.",
        "te": "దయచేసి మందు పేరు మరియు మోతాదును నమోదు చేయండి.",
        "hi": "कृपया दवा का नाम और खुराक दर्ज करें।"
    },
    "err_select_timing_slot": {
        "en": "Please select at least one timing slot.",
        "te": "దయచేసి కనీసం ఒక సమయాన్ని ఎంచుకోండి.",
        "hi": "कृपया कम से कम एक समय स्लॉट चुनें।"
    },
    "success_added_med": {
        "en": "Added {name} to schedule!",
        "te": "{name} మందును షెడ్యూల్‌కు జోడించాము!",
        "hi": "{name} दवा अनुसूची में जोड़ी गई!"
    },
    "select_log_date": {
        "en": "Select Date to View or Correct",
        "te": "చూడటానికి లేదా సవరించడానికి తేదీని ఎంచుకోండి",
        "hi": "तारीख चुनें"
    },
    "no_meds_for_date": {
        "en": "No active medications scheduled for {date}.",
        "te": "{date} నాడు ఎటువంటి మందులు షెడ్యూల్ చేయబడలేదు.",
        "hi": "{date} के लिए कोई दवा निर्धारित नहीं है।"
    },
    "adherence_7day": {
        "en": "7-Day Adherence Rate",
        "te": "7-రోజుల క్రమశిక్షణ శాతం",
        "hi": "7-दिवसीय अनुपालन दर"
    },
    "adherence_30day": {
        "en": "30-Day Adherence Rate",
        "te": "30-రోజుల క్రమశిక్షణ శాతం",
        "hi": "30-दिवसीय अनुपालन दर"
    },
    "adherence_sub": {
        "en": "{taken} taken, {skipped} skipped, {missed} missed",
        "te": "{taken} తీసుకున్నారు, {skipped} విడిచిపెట్టారు, {missed} మర్చిపోయారు",
        "hi": "{taken} ली गईं, {skipped} छोड़ी गईं, {missed} छूट गईं"
    },
    "chart_adherence_title": {
        "en": "30-Day Medication Adherence Breakdown",
        "te": "30-రోజుల మందుల క్రమ వివరాలు",
        "hi": "30-दिवसीय दवा अनुपालन"
    },

    # Appointment Manager
    "app_mgr_title": {
        "en": "🗓️ Medical Appointment Manager",
        "te": "🗓️ వైద్య అపాయింట్‌మెంట్‌ల నిర్వహణ",
        "hi": "🗓️ मेडिकल अपॉइंटमेंट प्रबंधक"
    },
    "app_mgr_caption": {
        "en": "Schedule and track upcoming doctor visits, specialist consultations, and past checkups.",
        "te": "వైద్యుల సందర్శనలను, స్పెషలిస్ట్ సంప్రదింపులను మరియు గత చెకప్‌లను షెడ్యూల్ చేయండి మరియు ట్రాక్ చేయండి.",
        "hi": "अपॉइंटमेंट्स शेड्यूल और ट्रैक करें।"
    },
    "tab_app_list": {
        "en": "📅 Upcoming & Past Appointments",
        "te": "📅 రాబోయే & గత అపాయింట్‌మెంట్‌లు",
        "hi": "📅 आगामी और पिछली अपॉइंटमेंट्स"
    },
    "tab_app_new": {
        "en": "➕ Schedule New Appointment",
        "te": "➕ కొత్త అపాయింట్‌మెంట్‌ను బుక్ చేయండి",
        "hi": "➕ नई अपॉइंटमेंट शेड्यूल करें"
    },
    "no_app_scheduled": {
        "en": "No appointments scheduled yet. Schedule your first appointment in the next tab.",
        "te": "ఇంకా అపాయింట్‌మెంట్‌లేవీ లేవు. తదుపరి ట్యాబ్‌లో మీ మొదటి అపాయింట్‌మెంట్‌ను బుక్ చేసుకోండి.",
        "hi": "कोई अपॉइंटमेंट निर्धारित नहीं है।"
    },
    "app_location": {
        "en": "Location",
        "te": "స్థలం",
        "hi": "स्थान"
    },
    "app_mode": {
        "en": "Mode",
        "te": "విధానం",
        "hi": "मोड"
    },
    "app_date": {
        "en": "Date",
        "te": "తేదీ",
        "hi": "तारीख"
    },
    "app_notes": {
        "en": "Notes",
        "te": "గమనికలు",
        "hi": "नोट्स"
    },
    "btn_mark_completed": {
        "en": "Mark Completed",
        "te": "పూర్తయినట్లు గుర్తించు",
        "hi": "पूर्ण चिह्नित करें"
    },
    "btn_cancel_visit": {
        "en": "Cancel Visit",
        "te": "సందర్శనను రద్దు చేయి",
        "hi": "रद्द करें"
    },
    "doc_name_spec_label": {
        "en": "Doctor Name & Specialization",
        "te": "వైద్యుని పేరు & ప్రత్యేకత",
        "hi": "डॉक्टर का नाम और विशेषज्ञता"
    },
    "clinic_label": {
        "en": "Clinic / Hospital Name",
        "te": "క్లినిక్ / ఆసుపత్రి పేరు",
        "hi": "क्लिनिक / अस्पताल का नाम"
    },
    "consult_mode_label": {
        "en": "Consultation Mode",
        "te": "సంప్రదింపు విధానం",
        "hi": "परामर्श मोड"
    },
    "mode_in_person": {
        "en": "In-Person",
        "te": "ప్రత్యక్షంగా (హాస్పిటల్‌లో)",
        "hi": "व्यक्तिगत रूप से"
    },
    "mode_video": {
        "en": "Video / Online",
        "te": "వీడియో / ఆన్‌లైన్",
        "hi": "वीडियो / ऑनलाइन"
    },
    "mode_phone": {
        "en": "Phone",
        "te": "ఫోన్ కాల్",
        "hi": "फ़ोन कॉल"
    },
    "app_date_label": {
        "en": "Appointment Date",
        "te": "అపాయింట్‌మెంట్ తేదీ",
        "hi": "अपॉइंटमेंट तिथि"
    },
    "app_time_label": {
        "en": "Appointment Time",
        "te": "అపాయింట్‌మెంట్ సమయం",
        "hi": "अपॉइंटमेंट समय"
    },
    "clinic_phone_label": {
        "en": "Clinic Contact Number",
        "te": "క్లినిక్ ఫోన్ నంబర్",
        "hi": "क्लिनिक संपर्क नंबर"
    },
    "notes_purpose_label": {
        "en": "Notes / Purpose of Visit",
        "te": "సందర్శన ఉద్దేశం / గమనికలు",
        "hi": "भेंट का उद्देश्य / नोट्स"
    },
    "btn_schedule_submit": {
        "en": "Confirm & Schedule Appointment",
        "te": "నిర్ధారించండి & అపాయింట్‌మెంట్‌ను బుక్ చేయండి",
        "hi": "पुष्टि करें और अपॉइंटमेंट तय करें"
    },
    "err_doc_clinic_req": {
        "en": "Please provide both doctor name and facility.",
        "te": "దయచేసి వైద్యుని పేరు మరియు ఆసుపత్రి రెండింటినీ నమోదు చేయండి.",
        "hi": "कृपया डॉक्टर का नाम और अस्पताल बताएं।"
    },
    "success_app_scheduled": {
        "en": "Appointment with {doctor} scheduled successfully!",
        "te": "{doctor} తో అపాయింట్‌మెంట్ విజయవంతంగా షెడ్యూల్ చేయబడింది!",
        "hi": "अपॉइंटमेंट सफलतापूर्वक तय हो गई!"
    },

    # Health History & PDF Export
    "hist_title": {
        "en": "📜 Health History & Archive",
        "te": "📜 ఆరోగ్య చరిత్ర & ఆర్కైవ్",
        "hi": "📜 स्वास्थ्य इतिहास और पुरालेख"
    },
    "hist_caption": {
        "en": "Search, filter, review past medical reports, and export monthly summary PDFs for your doctor.",
        "te": "గత వైద్య నివేదికలను శోధించండి, సమీక్షించండి మరియు మీ వైద్యుని కోసం నెలవారీ PDF సారాంశాన్ని పొందండి.",
        "hi": "पिछली रिपोर्ट खोजें और PDF बनाएं।"
    },
    "tab_hist_archive": {
        "en": "📂 Medical Reports Archive",
        "te": "📂 వైద్య నివేదికల ఆర్కైవ్",
        "hi": "📂 रिपोर्ट संग्रह"
    },
    "tab_hist_pdf": {
        "en": "📄 Monthly Summary PDF Export",
        "te": "📄 నెలవారీ సారాంశ PDF డౌన్‌లోడ్",
        "hi": "📄 मासिक सारांश PDF"
    },
    "no_reports_saved": {
        "en": "No medical reports saved yet. Upload your first report in the Medical Report Reader.",
        "te": "ఇంకా నివేదికలేవీ సేవ్ కాలేదు. మెడికల్ రిపోర్ట్ రీడర్‌లో మీ మొదటి నివేదికను అప్‌లోడ్ చేయండి.",
        "hi": "कोई रिपोर्ट नहीं मिली।"
    },
    "search_reports_placeholder": {
        "en": "🔍 Search reports by title or doctor",
        "te": "🔍 శీర్షిక లేదా వైద్యుని పేరుతో శోధించండి",
        "hi": "🔍 शीर्षक या डॉक्टर से खोजें"
    },
    "btn_delete_report": {
        "en": "🗑️ Delete Report",
        "te": "🗑️ నివేదికను తొలగించు",
        "hi": "🗑️ रिपोर्ट हटाएं"
    },
    "report_deleted_msg": {
        "en": "Report deleted.",
        "te": "నివేదిక తొలగించబడింది.",
        "hi": "रिपोर्ट हटाई गई।"
    },
    "pdf_gen_heading": {
        "en": "📄 Generate Official Monthly Health Summary PDF",
        "te": "📄 అధికారిక నెలవారీ ఆరోగ్య సారాంశ PDFని రూపొందించండి",
        "hi": "📄 आधिकारिक मासिक स्वास्थ्य सारांश PDF उत्पन्न करें"
    },
    "pdf_gen_caption": {
        "en": "Generates a clean, comprehensive PDF report with adherence stats, active medicines, test highlights, and safety disclaimers for consultation with your doctor.",
        "te": "మీ వైద్యుని సంప్రదింపుల కోసం మందుల క్రమం, ప్రస్తుత మందులు, కీలక పరీక్షలు మరియు భద్రతా సూచనలతో కూడిన సమగ్ర నివేదికను రూపొందిస్తుంది.",
        "hi": "डॉक्टर के परामर्श के लिए विस्तृत PDF।"
    },
    "year_label": {
        "en": "Year",
        "te": "సంవత్సరం",
        "hi": "वर्ष"
    },
    "month_label": {
        "en": "Month",
        "te": "నెల",
        "hi": "महीना"
    },
    "btn_generate_pdf": {
        "en": "📥 Generate & Download PDF Summary",
        "te": "📥 PDF సారాంశాన్ని రూపొందించండి & డౌన్‌లోడ్ చేయండి",
        "hi": "📥 PDF सारांश बनाएं और डाउनलोड करें"
    },
    "spinner_compiling_pdf": {
        "en": "Compiling monthly adherence, medicines, and diagnostic tests into PDF...",
        "te": "నెలవారీ మందుల క్రమం, పరీక్షలు మరియు వివరాలను PDFగా క్రోడీకరిస్తోంది...",
        "hi": "PDF तैयार किया जा रहा है..."
    },
    "pdf_success_msg": {
        "en": "🎉 Monthly health summary PDF compiled successfully!",
        "te": "🎉 నెలవారీ ఆరోగ్య సారాంశ PDF విజయవంతంగా రూపొందించబడింది!",
        "hi": "🎉 मासिक स्वास्थ्य सारांश PDF तैयार है!"
    },
    "btn_download_pdf_file": {
        "en": "⬇️ Click Here to Download PDF File",
        "te": "⬇️ PDF ఫైల్‌ను డౌన్‌లోడ్ చేయడానికి ఇక్కడ క్లిక్ చేయండి",
        "hi": "⬇️ PDF डाउनलोड करने के लिए यहाँ क्लिक करें"
    },
    "pdf_failed_msg": {
        "en": "Failed to generate PDF summary.",
        "te": "PDF సారాంశాన్ని రూపొందించడం విఫలమైంది.",
        "hi": "PDF बनाने में विफल।"
    },

    # Family Connections
    "fam_title": {
        "en": "👨‍👩‍👧 Family Connections & Secure Sharing",
        "te": "👨‍👩‍👧 కుటుంబ బంధాలు & సురక్షిత భాగస్వామ్యం",
        "hi": "👨‍👩‍👧 पारिवारिक संबंध और साझाकरण"
    },
    "fam_caption": {
        "en": "Securely connect parents and adult children. Children can only view health records after explicit parent approval.",
        "te": "తల్లిదండ్రులను మరియు పిల్లలను సురక్షితంగా అనుసంధానించండి. తల్లిదండ్రుల స్పష్టమైన అనుమతి తర్వాతే పిల్లలు ఆరోగ్య రికార్డులను చూడగలరు.",
        "hi": "माता-पिता और बच्चों को सुरक्षित रूप से जोड़ें।"
    },
    "fam_parent_portal": {
        "en": "👴 Parent Sharing Portal",
        "te": "👴 తల్లిదండ్రుల భాగస్వామ్య పోర్టల్",
        "hi": "👴 माता-पिता शेयरिंग पोर्टल"
    },
    "fam_parent_desc": {
        "en": "Invite your adult children or family caregivers to help monitor your medicine schedule and appointments. Generate a secure invitation code and share it with them.",
        "te": "మీ మందుల వేళలను మరియు అపాయింట్‌మెంట్‌లను పర్యవేక్షించడంలో సహాయం చేయడానికి మీ పిల్లలను లేదా సంరక్షకులను ఆహ్వానించండి. సురక్షిత ఆహ్వాన కోడ్‌ను సృష్టించి వారితో పంచుకోండి.",
        "hi": "अपने बच्चों या देखभाल करने वालों को आमंत्रित करें।"
    },
    "fam_relation_label": {
        "en": "Family Relationship",
        "te": "కుటుంబ సంబంధం",
        "hi": "पारिवारिक संबंध"
    },
    "rel_son": {
        "en": "Son",
        "te": "కుమారుడు",
        "hi": "बेटा"
    },
    "rel_daughter": {
        "en": "Daughter",
        "te": "కుమార్తె",
        "hi": "बेटी"
    },
    "rel_spouse": {
        "en": "Spouse",
        "te": "భార్య / భర్త",
        "hi": "जीवनसाथी"
    },
    "rel_caregiver": {
        "en": "Caregiver",
        "te": "సంరక్షకుడు",
        "hi": "देखभालकर्ता"
    },
    "btn_gen_invite": {
        "en": "🔑 Generate New Invitation Code",
        "te": "🔑 కొత్త ఆహ్వాన కోడ్‌ను సృష్టించండి",
        "hi": "🔑 नया आमंत्रण कोड बनाएं"
    },
    "fam_members_heading": {
        "en": "Connected Family Members & Pending Requests",
        "te": "అనుసంధానమైన కుటుంబ సభ్యులు & పెండింగ్ అభ్యర్థనలు",
        "hi": "जुड़े परिवार के सदस्य"
    },
    "no_invite_codes": {
        "en": "No invitation codes generated yet.",
        "te": "ఇంకా ఆహ్వాన కోడ్‌లేవీ సృష్టించబడలేదు.",
        "hi": "कोई आमंत्रण कोड नहीं बना है।"
    },
    "btn_approve_access": {
        "en": "✅ Approve Access",
        "te": "✅ అనుమతించు",
        "hi": "✅ पहुंच स्वीकृत करें"
    },
    "btn_reject_request": {
        "en": "❌ Reject Request",
        "te": "❌ తిరస్కరించు",
        "hi": "❌ अस्वीकार करें"
    },
    "btn_revoke_access": {
        "en": "🚫 Revoke Family Access",
        "te": "🚫 యాక్సెస్‌ను రద్దు చేయి",
        "hi": "🚫 पहुंच रद्द करें"
    },
    "fam_child_portal": {
        "en": "👧 Child / Caregiver Portal",
        "te": "👧 పిల్లలు / సంరక్షకుల పోర్టల్",
        "hi": "👧 बच्चा / देखभालकर्ता पोर्टल"
    },
    "fam_child_desc": {
        "en": "Enter the 8-character invitation code provided by your parent to request access.",
        "te": "యాక్సెస్ అభ్యర్థించడానికి మీ తల్లిదండ్రులు ఇచ్చిన 8-అక్షరాల ఆహ్వాన కోడ్‌ను నమోదు చేయండి.",
        "hi": "माता-पिता द्वारा दिया गया कोड दर्ज करें।"
    },
    "invite_code_label": {
        "en": "Parent Invitation Code",
        "te": "తల్లిదండ్రుల ఆహ్వాన కోడ్",
        "hi": "माता-पिता आमंत्रण कोड"
    },
    "btn_request_connect": {
        "en": "Request Connection to Parent",
        "te": "తల్లిదండ్రులకు కనెక్షన్ అభ్యర్థించండి",
        "hi": "माता-पिता से जुड़ने का अनुरोध करें"
    },
    "err_enter_invite_code": {
        "en": "Please enter an invitation code.",
        "te": "దయచేసి ఆహ్వాన కోడ్‌ను నమోదు చేయండి.",
        "hi": "कृपया आमंत्रण कोड दर्ज करें।"
    },
    "connected_parents_heading": {
        "en": "Your Connected Parents",
        "te": "మీరు కనెక్ట్ అయిన తల్లిదండ్రులు",
        "hi": "आपके जुड़े हुए माता-पिता"
    },
    "no_connected_parents": {
        "en": "You do not have any approved parent connections yet. Please enter an invitation code above.",
        "te": "మీకు ఇంకా ఆమోదించబడిన తల్లిదండ్రుల కనెక్షన్‌లు లేవు. దయచేసి పైన ఆహ్వాన కోడ్‌ను నమోదు చేయండి.",
        "hi": "कोई जुड़ा हुआ माता-पिता नहीं है।"
    },
    "badge_connected": {
        "en": "CONNECTED",
        "te": "కనెక్ట్ అయ్యారు",
        "hi": "जुड़े हुए हैं"
    },

    # Settings
    "settings_title": {
        "en": "⚙️ Profile & System Settings",
        "te": "⚙️ ప్రొఫైల్ & సిస్టమ్ సెట్టింగ్‌లు",
        "hi": "⚙️ प्रोफ़ाइल और सिस्टम सेटिंग्स"
    },
    "settings_caption": {
        "en": "Manage notifications, contact preferences, and review privacy security architecture.",
        "te": "నోటిఫికేషన్‌లు, సంప్రదింపు ప్రాధాన్యతలను నిర్వహించండి మరియు గోప్యతా భద్రతా విధానాలను సమీక్షించండి.",
        "hi": "सूचनाएं और सेटिंग्स प्रबंधित करें।"
    },
    "tab_set_profile": {
        "en": "👤 Profile & Notifications",
        "te": "👤 ప్రొఫైల్ & నోటిఫికేషన్‌లు",
        "hi": "👤 प्रोफ़ाइल और सूचनाएं"
    },
    "tab_set_telegram": {
        "en": "📲 Telegram Alerts Setup",
        "te": "📲 టెలిగ్రామ్ అలర్ట్స్ సెటప్",
        "hi": "📲 टेलीग्राम अलर्ट"
    },
    "tab_set_privacy": {
        "en": "🛡️ Privacy & Security Architecture",
        "te": "🛡️ గోప్యత & భద్రతా విధానం",
        "hi": "🛡️ गोपनीयता और सुरक्षा"
    },
    "user_profile_heading": {
        "en": "User Profile",
        "te": "వినియోగదారు ప్రొఫైల్",
        "hi": "उपयोगकर्ता प्रोफ़ाइल"
    },
    "tg_chat_id_label": {
        "en": "Telegram Chat ID",
        "te": "టెలిగ్రామ్ చాట్ ID",
        "hi": "टेलीग्राम चैट आईडी"
    },
    "tg_chat_id_help": {
        "en": "Get this by messaging @userinfobot or your HealthBuddy Telegram bot",
        "te": "@userinfobot లేదా మీ హెల్త్‌బడ్డీ టెలిగ్రామ్ బాట్‌కి మెసేజ్ చేయడం ద్వారా దీన్ని పొందండి",
        "hi": "टेलीग्राम बॉट से प्राप्त करें"
    },
    "notif_prefs_heading": {
        "en": "Notification Preferences",
        "te": "నోటిఫికేషన్ ప్రాధాన్యతలు",
        "hi": "सूचना प्राथमिकताएं"
    },
    "notif_med_reminders": {
        "en": "Receive Medicine Schedule Reminders",
        "te": "మందుల షెడ్యూల్ రిమైండర్‌లను స్వీకరించండి",
        "hi": "दवा रिमाइंडर प्राप्त करें"
    },
    "notif_app_reminders": {
        "en": "Receive Upcoming Appointment Reminders",
        "te": "రాబోయే అపాయింట్‌మెంట్ రిమైండర్‌లను స్వీకరించండి",
        "hi": "अपॉइंटमेंट रिमाइंडर प्राप्त करें"
    },
    "btn_save_profile": {
        "en": "Save Profile Settings",
        "te": "ప్రొఫైల్ సెట్టింగ్‌లను సేవ్ చేయండి",
        "hi": "सेटिंग्स सहेजें"
    },
    "profile_updated_success": {
        "en": "Profile settings updated successfully!",
        "te": "ప్రొఫైల్ సెట్టింగ్‌లు విజయవంతంగా నవీకరించబడ్డాయి!",
        "hi": "प्रोफ़ाइल अपडेट की गई!"
    },
    "tg_integration_heading": {
        "en": "📲 Telegram Bot Notification Integration",
        "te": "📲 టెలిగ్రామ్ బాట్ నోటిఫికేషన్ అనుసంధానం",
        "hi": "📲 टेलीग्राम बॉट एकीकरण"
    },
    "tg_integration_desc": {
        "en": "HealthBuddy can send discreet, timely medicine reminders (Morning: 08:00, Afternoon: 14:00, Night: 20:00 IST) and appointment alerts straight to your Telegram account.",
        "te": "హెల్త్‌బడ్డీ మీ టెలిగ్రామ్ ఖాతాకు నేరుగా సమయానికి మందుల రిమైండర్‌లను (ఉదయం: 08:00, మధ్యాహ్నం: 14:00, రాత్రి: 20:00 IST) మరియు అపాయింట్‌మెంట్ హెచ్చరికలను పంపగలదు.",
        "hi": "टेलीग्राम पर समय पर रिमाइंडर प्राप्त करें।"
    },
    "tg_id_configured": {
        "en": "Configured Telegram Chat ID",
        "te": "కాన్ఫిగర్ చేసిన టెలిగ్రామ్ చాట్ ID",
        "hi": "कॉन्फ़िगर की गई टेलीग्राम आईडी"
    },
    "tg_enable_hint": {
        "en": "To enable notifications, enter your Telegram Chat ID in the Profile tab.",
        "te": "నోటిఫికేషన్‌లను ప్రారంభించడానికి, ప్రొఫైల్ ట్యాబ్‌లో మీ టెలిగ్రామ్ చాట్ IDని నమోదు చేయండి.",
        "hi": "प्रोफ़ाइल टैब में चैट आईडी दर्ज करें।"
    },
    "btn_test_tg": {
        "en": "🧪 Send Test Telegram Ping",
        "te": "🧪 టెస్ట్ టెలిగ్రామ్ మెసేజ్ పంపండి",
        "hi": "🧪 टेस्ट टेलीग्राम संदेश भेजें"
    },
    "tg_dispatch_spinner": {
        "en": "Dispatching verification message...",
        "te": "ధృవీకరణ సందేశాన్ని పంపుతోంది...",
        "hi": "सत्यापन संदेश भेजा जा रहा है..."
    },
    "tg_ping_success": {
        "en": "✅ Test ping delivered! Check your Telegram app.",
        "te": "✅ టెస్ట్ సందేశం అందింది! మీ టెలిగ్రామ్ యాప్‌ను తనిఖీ చేయండి.",
        "hi": "✅ संदेश पहुंच गया!"
    },
    "privacy_heading": {
        "en": "🛡️ Privacy, Security & Data Protection Architecture",
        "te": "🛡️ గోప్యత, భద్రత & డేటా సంరక్షణ విధానం",
        "hi": "🛡️ गोपनीयता और डेटा सुरक्षा"
    },
    "privacy_bullets": {
        "en": """
- **Fernet Symmetric Encryption at Rest:** Extracted medical report data, sensitive clinical values, and doctor notes are encrypted using AES-128 in CBC mode with HMAC authentication.
- **Bcrypt Password Hashing:** User passwords are encrypted with individual cryptographic salts and never stored in plaintext.
- **Role-Based Server Authorization:** Every database operation strictly validates parent-child permissions. Children cannot view or modify parent records without an explicit, active `approved` status.
- **Login Rate Limiting:** Automatic lockout protects against automated brute force attempts.
- **File Integrity & Signature Validation:** Only verified PDF, PNG, and JPEG documents matching true magic byte headers are processed, preventing MIME spoofing.
- **Audit Trail Logging:** All sensitive security actions (logins, reports viewed, access revoked) are permanently recorded in `audit_logs`.
        """,
        "te": """
- **ఫెర్నెట్ సిమెట్రిక్ ఎన్‌క్రిప్షన్:** సేకరించిన వైద్య నివేదిక డేటా, సున్నితమైన ఆరోగ్య విలువలు మరియు వైద్యుని గమనికలు AES-128 CBC మోడ్ మరియు HMAC ప్రామాణీకరణతో భద్రపరచబడతాయి.
- **Bcrypt పాస్‌వర్డ్ హాషింగ్:** వినియోగదారు పాస్‌వర్డ్‌లు క్రిప్టోగ్రాఫిక్ సాల్ట్‌లతో భద్రపరచబడతాయి మరియు ప్లెయిన్‌టెక్స్ట్‌లో ఎప్పుడూ నిల్వ చేయబడవు.
- **పాత్ర-ఆధారిత సర్వర్ అనుమతులు:** తల్లిదండ్రుల స్పష్టమైన ఆమోదం లేకుండా పిల్లలు రికార్డులను చూడలేరు లేదా మార్చలేరు.
- **లాగిన్ రేట్ లిమిటింగ్:** బ్రూట్ ఫోర్స్ దాడుల నుండి ఆటోమేటిక్ రక్షణ.
- **ఫైల్ సమగ్రత ధృవీకరణ:** నిజమైన PDF, PNG, JPEG డాక్యుమెంట్లు మాత్రమే ప్రాసెస్ చేయబడతాయి.
- **ఆడిట్ ట్రయిల్ లాగింగ్:** అన్ని కీలక భద్రతా చర్యలు `audit_logs`లో శాశ్వతంగా నమోదు చేయబడతాయి.
        """,
        "hi": """
- **Fernet एन्क्रिप्शन:** डेटा सुरक्षित रूप से एन्क्रिप्ट किया गया है।
- **Bcrypt पासवर्ड:** पासवर्ड सुरक्षित रूप से हैश किए जाते हैं।
- **भूमिका-आधारित पहुंच:** केवल स्वीकृत सदस्य ही देख सकते हैं।
        """
    },

    # Footer
    "footer_rights": {
        "en": "© 2026 HealthBuddy. All rights reserved. Compassionate Care for Families.",
        "te": "© 2026 హెల్త్‌బడ్డీ. సర్వహక్కులు ప్రత్యేకించబడ్డాయి. కుటుంబాల కోసం ఆప్యాయమైన సంరక్షణ.",
        "hi": "© 2026 हेल्थबडी। सर्वाधिकार सुरक्षित। परिवारों के लिए देखभाल।"
    },
    "footer_disclaimer": {
        "en": "Informational only. Not a substitute for professional medical advice, diagnosis, or treatment.",
        "te": "సమాచారం కొరకు మాత్రమే. వృత్తిపరమైన వైద్య సలహా, రోగనిర్ధారణ లేదా చికిత్సకు ప్రత్యామ్నాయం కాదు.",
        "hi": "केवल सूचनात्मक उद्देश्य के लिए।"
    }
}

def t(key: str, lang: str = "en", **kwargs) -> str:
    """Gets localized text string with fallback to English and optional formatting."""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("en", key))
    if kwargs and isinstance(text, str):
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

def generate_tts_audio(text: str, lang: str = "en") -> Optional[bytes]:
    """
    Generates text-to-speech audio bytes using gTTS in memory.
    Handles 'en', 'hi', 'te'.
    Returns None gracefully if offline or in case of network timeout.
    """
    if not text or not text.strip():
        return None

    # Map lang to gTTS supported code
    gtts_lang = "en"
    if lang == "hi":
        gtts_lang = "hi"
    elif lang == "te":
        gtts_lang = "te"

    try:
        # Clean text snippet (limit to 1200 characters for snappy playback)
        speech_text = text.strip()[:1200]
        tts = gTTS(text=speech_text, lang=gtts_lang, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp.read()
    except Exception as e:
        logger.warning(f"Could not generate TTS audio (network might be offline): {e}")
        return None
