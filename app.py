import os
import json
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# Internal Modules
import config
from database import init_db, execute_query, execute_one, log_audit
from auth import (
    register_user,
    login_user,
    get_user_by_id,
    update_user_profile,
    check_parent_access,
)
from report_service import (
    process_uploaded_document_to_images,
    save_medical_report,
    get_user_reports,
    get_report_details,
    delete_medical_report,
)
from ai_service import analyze_medical_document, ReportExplanation, MANDATORY_DISCLAIMER, MANDATORY_DISCLAIMER_TE
from medicine_service import (
    add_medicine,
    update_medicine,
    delete_medicine,
    get_user_medicines,
    log_dose,
    get_daily_schedule_with_logs,
    get_adherence_stats,
    MISSED_DOSE_SAFETY_RULE,
    MISSED_DOSE_SAFETY_RULE_HI,
    MISSED_DOSE_SAFETY_RULE_TE,
)
from appointment_service import (
    add_appointment,
    update_appointment,
    cancel_appointment,
    update_appointment_status,
    get_user_appointments,
)
from family_service import (
    generate_invite_code,
    connect_with_invite_code,
    update_link_status,
    get_parent_family_members,
    get_child_connected_parents,
)
from notification_service import send_test_telegram_ping
from scheduler import start_background_scheduler
from pdf_service import generate_monthly_health_summary_pdf
from i18n import t, generate_tts_audio
from seed_data import seed_sample_data_if_empty

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="HealthBuddy for Parents",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize Database and Background Scheduler once
@st.cache_resource
def setup_services():
    init_db()
    seed_sample_data_if_empty()
    try:
        start_background_scheduler()
    except Exception as e:
        print(f"Scheduler setup notice: {e}")
    return True

setup_services()

# Custom CSS for Modern, Clean Healthcare Dashboard & Cyber Glassmorphism 3D
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* Hide Default Streamlit Top Header & Sidebar */
    header[data-testid="stHeader"], .stAppHeader {
        background-color: transparent !important;
        background: transparent !important;
        color: transparent !important;
        height: 0px !important;
    }
    
    section[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
    }
    
    /* Global Base - Transparent so 3D canvas shines through */
    html, body, [class*="css"], .stApp, .stMarkdown, .stText, p, span, div, button, input, select, textarea, label {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Telugu', 'Gautami', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #030810 !important;
        color: #F1F5F9 !important;
    }

    /* Deep Space Background - 3D canvas renders over this */
    .stApp {
        background: #030810 !important;
        background-attachment: fixed !important;
    }

    /* Primary Container Styling */
    .main .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 6rem !important;
        max-width: 980px !important;
    }

    /* Top Navigation Bar */
    .top-navbar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 0.2rem;
        margin-bottom: 1.2rem;
    }
    .brand-title {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 1.6rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
    }
    .brand-title span.icon {
        color: #06B6D4;
        font-size: 1.8rem;
        filter: drop-shadow(0 0 10px #06B6D4);
    }

    /* User Pill */
    .user-badge-pill {
        background: rgba(13, 27, 46, 0.85);
        border: 1px solid rgba(20, 184, 166, 0.3);
        border-radius: 9999px;
        padding: 0.45rem 1.15rem;
        font-size: 0.95rem;
        font-weight: 600;
        color: #E2E8F0;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        backdrop-filter: blur(14px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    /* Hero Greeting */
    .hero-greeting-text {
        font-size: 2.3rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 1.2rem;
        letter-spacing: -0.03em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    /* Glassmorphism Card Components */
    .health-card, .glass-card {
        background: rgba(13, 27, 46, 0.72) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(20, 184, 166, 0.25) !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
        color: #F8FAFC !important;
        padding: 1.5rem !important;
        margin-bottom: 1.1rem !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }
    .health-card:hover, .glass-card:hover {
        border-color: rgba(6, 182, 212, 0.5) !important;
        box-shadow: 0 12px 36px rgba(6, 182, 212, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
    }

    /* Stats Quick Cards */
    .stat-glass-box {
        background: rgba(13, 27, 46, 0.72);
        border: 1px solid rgba(20, 184, 166, 0.22);
        border-radius: 18px;
        padding: 1.3rem 1rem;
        text-align: center;
        backdrop-filter: blur(14px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        transition: all 0.2s ease;
    }
    .stat-glass-box:hover {
        border-color: #06B6D4;
        transform: translateY(-2px);
    }
    .stat-number {
        font-size: 2.3rem;
        font-weight: 800;
        color: #06B6D4;
        line-height: 1.1;
        text-shadow: 0 0 16px rgba(6, 182, 212, 0.45);
    }
    .stat-label {
        font-size: 0.95rem;
        color: #94A3B8;
        font-weight: 600;
        margin-top: 0.35rem;
    }

    /* CTA Hint Banner */
    .cta-banner {
        background: rgba(13, 30, 48, 0.85);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-left: 6px solid #10B981;
        border-radius: 14px;
        padding: 0.95rem 1.3rem;
        color: #F8FAFC;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15);
    }

    /* Streamlit Buttons Styled as Neon Pills */
    .stButton>button {
        background: linear-gradient(135deg, rgba(13, 148, 136, 0.9) 0%, rgba(6, 182, 212, 0.9) 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(6, 182, 212, 0.4) !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.3rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 14px rgba(6, 182, 212, 0.25) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5) !important;
        border-color: #38BDF8 !important;
    }

    /* Bottom Floating Dock Bar */
    .floating-dock-bar {
        position: fixed;
        bottom: 1rem;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(10, 22, 38, 0.92);
        border: 1px solid rgba(20, 184, 166, 0.35);
        border-radius: 9999px;
        padding: 0.5rem 1rem;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7), 0 0 24px rgba(6, 182, 212, 0.2);
        display: flex;
        gap: 0.8rem;
        z-index: 9999;
    }

    /* Inputs in Dark Theme */
    .stTextInput input, .stSelectbox [data-baseweb="select"], .stTextArea textarea {
        background-color: rgba(11, 23, 40, 0.85) !important;
        color: #F1F5F9 !important;
        border: 1px solid rgba(20, 184, 166, 0.3) !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus, .stTextArea textarea:focus {
        border-color: #06B6D4 !important;
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.35) !important;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-normal { background-color: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-watch { background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-urgent { background-color: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-unknown { background-color: rgba(148, 163, 184, 0.2); color: #94A3B8; border: 1px solid rgba(148, 163, 184, 0.4); }

    /* Alert and Disclaimer */
    .safety-alert {
        background-color: rgba(30, 24, 12, 0.85);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-left: 5px solid #F59E0B;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        color: #FDE68A;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    .disclaimer-box {
        background-color: rgba(11, 23, 40, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        font-size: 0.82rem;
        color: #94A3B8;
        line-height: 1.5;
        margin-top: 1.2rem;
        margin-bottom: 1rem;
    }

    /* Sidebar Dark Theme */
    section[data-testid="stSidebar"] {
        background-color: #060E1A !important;
        border-right: 1px solid rgba(20, 184, 166, 0.18) !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---- 3D ANIMATED BACKGROUND (Three.js WebGL - DNA Helix + Particle Nebula) ----
THREEJS_BG = """
<style>
  #threejs-bg-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none;
  }
  /* Ensure Streamlit content floats above the 3D canvas */
  .stApp > * {
    position: relative;
    z-index: 1;
  }
  [data-testid="stAppViewContainer"] > section {
    position: relative;
    z-index: 2;
  }
  /* Animated floating orb glow effect */
  @keyframes orb-pulse {
    0%, 100% { opacity: 0.4; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.08); }
  }
  .bg-orb {
    position: fixed;
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: orb-pulse 6s ease-in-out infinite;
    filter: blur(80px);
  }
  .orb-teal {
    width: 520px; height: 520px;
    background: radial-gradient(circle, rgba(13,148,136,0.28) 0%, transparent 70%);
    top: -100px; right: -80px;
    animation-delay: 0s;
  }
  .orb-indigo {
    width: 460px; height: 460px;
    background: radial-gradient(circle, rgba(99,102,241,0.22) 0%, transparent 70%);
    bottom: 40px; left: -100px;
    animation-delay: -3s;
  }
  .orb-cyan {
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(6,182,212,0.18) 0%, transparent 70%);
    top: 45%; left: 42%;
    animation-delay: -1.5s;
    animation-duration: 8s;
  }
</style>

<!-- Ambient glow orbs (CSS-only backup behind Three.js) -->
<div class="bg-orb orb-teal"></div>
<div class="bg-orb orb-indigo"></div>
<div class="bg-orb orb-cyan"></div>

<canvas id="threejs-bg-canvas"></canvas>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function() {
  var canvas = document.getElementById('threejs-bg-canvas');
  if (!canvas) return;

  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x030810, 1);

  var scene = new THREE.Scene();

  var camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
  camera.position.set(0, 0, 120);

  // ---- Starfield particles ----
  var starGeo = new THREE.BufferGeometry();
  var starCount = 1800;
  var starPositions = new Float32Array(starCount * 3);
  var starSizes = new Float32Array(starCount);
  for (var i = 0; i < starCount; i++) {
    starPositions[i * 3]     = (Math.random() - 0.5) * 800;
    starPositions[i * 3 + 1] = (Math.random() - 0.5) * 800;
    starPositions[i * 3 + 2] = (Math.random() - 0.5) * 600;
    starSizes[i] = Math.random() * 1.8 + 0.4;
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
  starGeo.setAttribute('size', new THREE.BufferAttribute(starSizes, 1));

  var starMat = new THREE.PointsMaterial({
    color: 0xA8D8EA,
    size: 1.2,
    transparent: true,
    opacity: 0.55,
    sizeAttenuation: true,
  });
  var stars = new THREE.Points(starGeo, starMat);
  scene.add(stars);

  // ---- Floating molecule nodes (glowing spheres) ----
  var nodeGroup = new THREE.Group();
  var nodeCount = 28;
  var nodePositions = [];
  var nodeMeshes = [];
  var colors = [0x0D9488, 0x06B6D4, 0x6366F1, 0x10B981, 0x38BDF8, 0x818CF8];

  for (var j = 0; j < nodeCount; j++) {
    var geo = new THREE.SphereGeometry(Math.random() * 1.6 + 0.6, 16, 16);
    var col = colors[Math.floor(Math.random() * colors.length)];
    var mat = new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.7 });
    var mesh = new THREE.Mesh(geo, mat);
    var pos = {
      x: (Math.random() - 0.5) * 160,
      y: (Math.random() - 0.5) * 120,
      z: (Math.random() - 0.5) * 80,
      vx: (Math.random() - 0.5) * 0.04,
      vy: (Math.random() - 0.5) * 0.04,
      vz: (Math.random() - 0.5) * 0.025,
    };
    mesh.position.set(pos.x, pos.y, pos.z);
    nodeGroup.add(mesh);
    nodePositions.push(pos);
    nodeMeshes.push(mesh);
  }
  scene.add(nodeGroup);

  // ---- Connection lines between nearby nodes ----
  var lineGroup = new THREE.Group();
  scene.add(lineGroup);

  function updateLines() {
    while (lineGroup.children.length > 0) {
      lineGroup.remove(lineGroup.children[0]);
    }
    for (var a = 0; a < nodeMeshes.length; a++) {
      for (var b = a + 1; b < nodeMeshes.length; b++) {
        var dx = nodeMeshes[a].position.x - nodeMeshes[b].position.x;
        var dy = nodeMeshes[a].position.y - nodeMeshes[b].position.y;
        var dz = nodeMeshes[a].position.z - nodeMeshes[b].position.z;
        var dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
        if (dist < 42) {
          var opacity = (1 - dist / 42) * 0.38;
          var lineMat = new THREE.LineBasicMaterial({ color: 0x06B6D4, transparent: true, opacity: opacity });
          var points = [nodeMeshes[a].position.clone(), nodeMeshes[b].position.clone()];
          var lineGeo = new THREE.BufferGeometry().setFromPoints(points);
          lineGroup.add(new THREE.Line(lineGeo, lineMat));
        }
      }
    }
  }

  // ---- DNA Helix strand ----
  var helixGroup = new THREE.Group();
  scene.add(helixGroup);
  var helixPoints = 120;
  var helixRadius = 18;
  var helixHeight = 130;
  var dnaColors = [0x0D9488, 0x6366F1];

  for (var s = 0; s < 2; s++) {
    var helixGeo = new THREE.BufferGeometry();
    var hPositions = new Float32Array(helixPoints * 3);
    var offset = s === 0 ? 0 : Math.PI;
    for (var p = 0; p < helixPoints; p++) {
      var t = p / helixPoints;
      hPositions[p * 3]     = Math.cos(t * Math.PI * 6 + offset) * helixRadius;
      hPositions[p * 3 + 1] = t * helixHeight - helixHeight / 2;
      hPositions[p * 3 + 2] = Math.sin(t * Math.PI * 6 + offset) * helixRadius;
    }
    helixGeo.setAttribute('position', new THREE.BufferAttribute(hPositions, 3));
    var helixMat = new THREE.LineBasicMaterial({ color: dnaColors[s], transparent: true, opacity: 0.45, linewidth: 2 });
    helixGroup.add(new THREE.Line(helixGeo, helixMat));
  }

  // Cross rungs of DNA
  for (var r = 0; r < 22; r++) {
    var t2 = r / 22;
    var rungGeo = new THREE.BufferGeometry();
    var rPts = new Float32Array(6);
    var angle1 = t2 * Math.PI * 6;
    var angle2 = angle1 + Math.PI;
    var yRung = t2 * helixHeight - helixHeight / 2;
    rPts[0] = Math.cos(angle1) * helixRadius; rPts[1] = yRung; rPts[2] = Math.sin(angle1) * helixRadius;
    rPts[3] = Math.cos(angle2) * helixRadius; rPts[4] = yRung; rPts[5] = Math.sin(angle2) * helixRadius;
    rungGeo.setAttribute('position', new THREE.BufferAttribute(rPts, 3));
    var rungMat = new THREE.LineBasicMaterial({ color: 0x10B981, transparent: true, opacity: 0.25 });
    helixGroup.add(new THREE.Line(rungGeo, rungMat));
  }

  helixGroup.position.set(-60, 0, -30);
  helixGroup.rotation.z = 0.3;

  // ---- Mouse parallax ----
  var mouse = { x: 0, y: 0 };
  document.addEventListener('mousemove', function(e) {
    mouse.x = (e.clientX / window.innerWidth - 0.5) * 2;
    mouse.y = -(e.clientY / window.innerHeight - 0.5) * 2;
  });

  // ---- Resize handler ----
  window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // ---- Animation Loop ----
  var clock = new THREE.Clock();
  var lineUpdateTimer = 0;

  function animate() {
    requestAnimationFrame(animate);
    var elapsed = clock.getElapsedTime();

    // Rotate starfield slowly
    stars.rotation.y = elapsed * 0.012;
    stars.rotation.x = elapsed * 0.006;

    // Rotate DNA helix
    helixGroup.rotation.y = elapsed * 0.22;

    // Move nodes
    for (var n = 0; n < nodePositions.length; n++) {
      var np = nodePositions[n];
      np.x += np.vx; np.y += np.vy; np.z += np.vz;
      if (Math.abs(np.x) > 80) np.vx *= -1;
      if (Math.abs(np.y) > 60) np.vy *= -1;
      if (Math.abs(np.z) > 40) np.vz *= -1;
      nodeMeshes[n].position.set(np.x, np.y, np.z);
      // Pulse size
      var s = 1 + Math.sin(elapsed * 1.5 + n) * 0.18;
      nodeMeshes[n].scale.setScalar(s);
    }

    // Update connection lines every 6 frames
    lineUpdateTimer++;
    if (lineUpdateTimer % 6 === 0) updateLines();

    // Camera mouse parallax
    camera.position.x += (mouse.x * 12 - camera.position.x) * 0.03;
    camera.position.y += (mouse.y * 8  - camera.position.y) * 0.03;
    camera.lookAt(0, 0, 0);

    renderer.render(scene, camera);
  }
  animate();
})();
</script>
"""

st.markdown(THREEJS_BG, unsafe_allow_html=True)

# ----------------- Session State & Language Management -----------------
# 1. URL Query Parameter -> LocalStorage synchronization
query_lang = st.query_params.get("lang")
if query_lang in config.SUPPORTED_LANGUAGES:
    active_lang = query_lang
elif "preferred_lang" in st.session_state and st.session_state.preferred_lang in config.SUPPORTED_LANGUAGES:
    active_lang = st.session_state.preferred_lang
elif "user" in st.session_state and st.session_state.user and st.session_state.user.get("preferred_lang") in config.SUPPORTED_LANGUAGES:
    active_lang = st.session_state.user.get("preferred_lang")
else:
    active_lang = "en"

st.session_state.preferred_lang = active_lang
if st.query_params.get("lang") != active_lang:
    st.query_params["lang"] = active_lang

if "user" not in st.session_state:
    st.session_state.user = None
if "active_parent_id" not in st.session_state:
    st.session_state.active_parent_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

def set_language(new_lang: str):
    if new_lang in config.SUPPORTED_LANGUAGES and new_lang != st.session_state.preferred_lang:
        st.session_state.preferred_lang = new_lang
        st.query_params["lang"] = new_lang
        if st.session_state.user:
            try:
                update_user_profile(
                    user_id=st.session_state.user["id"],
                    full_name=st.session_state.user["full_name"],
                    preferred_lang=new_lang
                )
                st.session_state.user["preferred_lang"] = new_lang
            except Exception:
                pass
        st.rerun()

def logout():
    st.session_state.user = None
    st.session_state.active_parent_id = None
    st.rerun()

# Inject localStorage sync script to preserve language across refreshes and new tabs
LOCAL_STORAGE_SCRIPT = f"""
<script>
(function() {{
    var currentLang = "{st.session_state.preferred_lang}";
    try {{
        localStorage.setItem("healthbuddy_lang", currentLang);
    }} catch(e) {{}}
    
    // Check if URL has no lang parameter but localStorage has a saved choice
    var params = new URLSearchParams(window.location.search);
    var urlLang = params.get("lang");
    var savedLang = null;
    try {{
        savedLang = localStorage.getItem("healthbuddy_lang");
    }} catch(e) {{}}
    
    if (!savedLang && !urlLang) {{
        try {{ localStorage.setItem("healthbuddy_lang", "en"); }} catch(e) {{}}
    }} else if (!urlLang && savedLang && (savedLang === "en" || savedLang === "te") && savedLang !== currentLang) {{
        params.set("lang", savedLang);
        window.location.search = params.toString();
    }}
}})();
</script>
"""
st.markdown(LOCAL_STORAGE_SCRIPT, unsafe_allow_html=True)

# ----------------- Authentication Screens -----------------
def render_auth_view():
    lang = st.session_state.preferred_lang

    # Top Language Selector on Login Screen
    col_auth_left, col_auth_lang = st.columns([5, 2])
    with col_auth_lang:
        auth_lang_choice = st.selectbox(
            t("lang_selector_label", lang),
            options=list(config.SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: config.SUPPORTED_LANGUAGES[x],
            index=list(config.SUPPORTED_LANGUAGES.keys()).index(lang) if lang in config.SUPPORTED_LANGUAGES else 0,
            label_visibility="collapsed",
            key="auth_lang_switcher"
        )
        if auth_lang_choice != lang:
            set_language(auth_lang_choice)

    st.markdown(f"""
        <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 2rem;">
            <h1 style="font-size: 2.6rem; color: #FFFFFF; margin-bottom: 0.3rem; text-shadow: 0 0 20px rgba(6, 182, 212, 0.4);">{t("auth_welcome_title", lang)}</h1>
            <p style="font-size: 1.15rem; color: #94A3B8; max-width: 650px; margin: auto; line-height: 1.6;">
                {t("auth_welcome_desc", lang)}
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab1, auth_tab2, auth_tab3 = st.tabs([
            t("tab_login", lang),
            t("tab_register", lang),
            t("tab_demo", lang)
        ])

        # Tab 1: Log In
        with auth_tab1:
            st.markdown(f"#### {t('login_heading', lang)}")
            with st.form("login_form"):
                email = st.text_input(t("email_label", lang), placeholder=t("email_placeholder", lang))
                password = st.text_input(t("password_label", lang), type="password", placeholder=t("password_placeholder", lang))
                submitted = st.form_submit_button(t("login_button", lang), use_container_width=True)

                if submitted:
                    if not email or not password:
                        st.error(t("err_enter_email_pass", lang))
                    else:
                        success, message, user_data = login_user(email, password)
                        if success and user_data:
                            st.session_state.user = user_data
                            u_lang = user_data.get("preferred_lang", lang)
                            if u_lang in config.SUPPORTED_LANGUAGES:
                                st.session_state.preferred_lang = u_lang
                                st.query_params["lang"] = u_lang
                            if user_data["role"] == "parent":
                                st.session_state.active_parent_id = user_data["id"]
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

        # Tab 2: Register
        with auth_tab2:
            st.markdown(f"#### {t('register_heading', lang)}")
            with st.form("register_form"):
                reg_name = st.text_input(t("full_name_label", lang), placeholder=t("full_name_placeholder", lang))
                reg_email = st.text_input(t("email_label", lang), placeholder=t("email_placeholder", lang))
                reg_pass = st.text_input(t("password_label", lang), type="password", help=t("password_help", lang))
                reg_role = st.selectbox(
                    t("role_label", lang),
                    options=["parent", "child"],
                    format_func=lambda x: t("role_parent_option", lang) if x == "parent" else t("role_child_option", lang)
                )
                reg_phone = st.text_input(t("phone_label", lang), placeholder=t("phone_placeholder", lang))
                reg_lang = st.selectbox(
                    t("preferred_lang_label", lang),
                    options=list(config.SUPPORTED_LANGUAGES.keys()),
                    format_func=lambda x: config.SUPPORTED_LANGUAGES[x],
                    index=list(config.SUPPORTED_LANGUAGES.keys()).index(lang) if lang in config.SUPPORTED_LANGUAGES else 0
                )
                reg_submit = st.form_submit_button(t("register_button", lang), use_container_width=True)

                if reg_submit:
                    success, message, user_data = register_user(
                        email=reg_email,
                        password=reg_pass,
                        full_name=reg_name,
                        role=reg_role,
                        phone=reg_phone,
                        preferred_lang=reg_lang
                    )
                    if success and user_data:
                        st.session_state.user = user_data
                        st.session_state.preferred_lang = reg_lang
                        st.query_params["lang"] = reg_lang
                        if user_data["role"] == "parent":
                            st.session_state.active_parent_id = user_data["id"]
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        # Tab 3: Quick Demo Access
        with auth_tab3:
            st.markdown(f"#### {t('demo_heading', lang)}")
            st.info(t("demo_info", lang))
            
            c_p, c_c = st.columns(2)
            with c_p:
                if st.button(t("demo_parent_btn", lang), use_container_width=True):
                    _, _, u = login_user("parent@healthbuddy.com", "Password123!")
                    if u:
                        st.session_state.user = u
                        st.session_state.active_parent_id = u["id"]
                        st.session_state.preferred_lang = lang
                        st.query_params["lang"] = lang
                        st.rerun()

            with c_c:
                if st.button(t("demo_child_btn", lang), use_container_width=True):
                    _, _, u = login_user("child@healthbuddy.com", "Password123!")
                    if u:
                        st.session_state.user = u
                        st.session_state.preferred_lang = lang
                        st.query_params["lang"] = lang
                        # Set active parent to first approved parent
                        connected = get_child_connected_parents(u["id"])
                        if connected:
                            st.session_state.active_parent_id = connected[0]["parent_id"]
                        st.rerun()

            st.caption(t("demo_creds_caption", lang))

# ----------------- Top Header & Navigation -----------------
def render_top_navbar():
    user = st.session_state.user
    lang = st.session_state.preferred_lang

    col_nav_brand, col_nav_controls = st.columns([3, 2])
    with col_nav_brand:
        st.markdown(f"""
            <div class="top-navbar-container">
                <div class="brand-title">
                    <span class="icon">🩺</span> {t("app_title", lang)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col_nav_controls:
        c_user_pill, c_lang_sel = st.columns([3, 2])
        with c_user_pill:
            # If child, allow switching parent
            if user["role"] == "child":
                connected_parents = get_child_connected_parents(user["id"])
                if connected_parents:
                    p_opts = {p["parent_id"]: p["parent_name"] for p in connected_parents}
                    sel_p = st.selectbox(
                        t("parent_switcher_label", lang),
                        options=list(p_opts.keys()),
                        format_func=lambda x: f"👴 {p_opts[x]}",
                        label_visibility="collapsed",
                        key="top_parent_switcher"
                    )
                    st.session_state.active_parent_id = sel_p
                else:
                    st.markdown(f"""
                        <div style="text-align: right; margin-top: 0.5rem;">
                            <div class="user-badge-pill">
                                <span>{user['full_name']}</span>
                                <span style="color: #94A3B8; font-size: 0.8rem;">▾</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.session_state.active_parent_id = user["id"]
                st.markdown(f"""
                    <div style="text-align: right; margin-top: 0.5rem;">
                        <div class="user-badge-pill">
                            <span>{user['full_name']}</span>
                            <span style="color: #94A3B8; font-size: 0.8rem;">▾</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        with c_lang_sel:
            st.markdown("<div style='margin-top: 0.35rem;'>", unsafe_allow_html=True)
            new_lang = st.selectbox(
                t("lang_selector_label", lang),
                options=list(config.SUPPORTED_LANGUAGES.keys()),
                format_func=lambda x: config.SUPPORTED_LANGUAGES[x],
                index=list(config.SUPPORTED_LANGUAGES.keys()).index(lang) if lang in config.SUPPORTED_LANGUAGES else 0,
                label_visibility="collapsed",
                key="top_lang_sel"
            )
            if new_lang != lang:
                set_language(new_lang)
            st.markdown("</div>", unsafe_allow_html=True)


# ----------------- MORE NAVIGATION HUB -----------------
def render_more_hub(parent_id: int):
    lang = st.session_state.preferred_lang

    st.markdown(f"## {t('more_hub_title', lang)}")
    st.caption(t("more_hub_caption", lang))
    
    m1, m2 = st.columns(2)
    with m1:
        st.markdown('<div class="health-card">', unsafe_allow_html=True)
        st.markdown(f"### {t('hub_app_title', lang)}")
        st.markdown(t("hub_app_desc", lang))
        if st.button(t("hub_app_btn", lang), key="go_app_btn", use_container_width=True):
            st.session_state.current_page = "Appointment Manager"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="health-card">', unsafe_allow_html=True)
        st.markdown(f"### {t('hub_fam_title', lang)}")
        st.markdown(t("hub_fam_desc", lang))
        if st.button(t("hub_fam_btn", lang), key="go_fam_btn", use_container_width=True):
            st.session_state.current_page = "Family Connections"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with m2:
        st.markdown('<div class="health-card">', unsafe_allow_html=True)
        st.markdown(f"### {t('hub_hist_title', lang)}")
        st.markdown(t("hub_hist_desc", lang))
        if st.button(t("hub_hist_btn", lang), key="go_hist_btn", use_container_width=True):
            st.session_state.current_page = "Health History"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="health-card">', unsafe_allow_html=True)
        st.markdown(f"### {t('hub_set_title', lang)}")
        st.markdown(t("hub_set_desc", lang))
        if st.button(t("hub_set_btn", lang), key="go_set_btn", use_container_width=True):
            st.session_state.current_page = "Settings"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(t("logout_btn", lang), key="hub_logout_btn", use_container_width=True):
        logout()

# ----------------- PAGE 1: DASHBOARD -----------------
def render_dashboard(parent_id: int):
    user = st.session_state.user
    lang = st.session_state.preferred_lang

    if not parent_id:
        st.warning(t("dashboard_connect_parent_warning", lang))
        return

    # Check authorization
    if not check_parent_access(user, parent_id):
        st.error(t("dashboard_access_denied", lang))
        return

    parent_profile = get_user_by_id(parent_id)
    parent_name = parent_profile["full_name"] if parent_profile else "Parent"

    # Fetch metric statistics
    reports = get_user_reports(parent_id, user)
    medicines = get_user_medicines(parent_id, user, active_only=True)
    today_str = date.today().isoformat()
    today_schedule = get_daily_schedule_with_logs(parent_id, today_str, user)
    appointments = get_user_appointments(parent_id, user, status_filter="upcoming")

    total_today = len(today_schedule)
    taken_today = sum(1 for item in today_schedule if item["status"] == "taken")
    adherence_pct = round((taken_today / total_today * 100), 1) if total_today > 0 else 100.0

    # 2. Greeting Header
    st.markdown(f'<div class="hero-greeting-text">{t("dashboard_greeting", lang)}</div>', unsafe_allow_html=True)

    # 3. Health Score Hero Glass Card (Matching circular ring)
    score = int(adherence_pct)
    dash_offset = int(289 - (289 * (score / 100.0)))

    st.markdown(f"""
        <div class="health-card" style="display: flex; align-items: center; gap: 2rem; padding: 1.8rem 2.2rem; margin-bottom: 1.2rem;">
            <div style="position: relative; width: 115px; height: 115px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
                <svg width="115" height="115" viewBox="0 0 110 110" style="transform: rotate(-90deg);">
                    <circle cx="55" cy="55" r="46" stroke="rgba(20, 184, 166, 0.16)" stroke-width="9" fill="transparent" />
                    <circle cx="55" cy="55" r="46" stroke="#10B981" stroke-width="9" fill="transparent"
                            stroke-dasharray="289" stroke-dashoffset="{dash_offset}"
                            stroke-linecap="round" style="filter: drop-shadow(0 0 8px #10B981);" />
                </svg>
                <div style="position: absolute; font-size: 2.2rem; font-weight: 800; color: #FFFFFF; text-shadow: 0 0 16px rgba(16, 185, 129, 0.8);">
                    {score}
                </div>
            </div>
            <div>
                <div style="font-size: 1.75rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">{t('health_score_title', lang)}</div>
                <div style="font-size: 1.05rem; font-weight: 600; color: #94A3B8; margin-top: 0.2rem;">{t('health_score_adherence', lang, score=score)}</div>
                <div style="font-size: 0.88rem; color: #64748B; margin-top: 0.6rem; line-height: 1.5;">
                    {t('health_score_desc', lang)}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 4. Stats Row (3 Glass Cards: Reports, Medicines, Appointments)
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
            <div class="stat-glass-box">
                <div class="stat-number">{len(reports)}</div>
                <div class="stat-label">{t('card_reports_short', lang)}</div>
            </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
            <div class="stat-glass-box">
                <div class="stat-number">{len(medicines)}</div>
                <div class="stat-label">{t('card_medicines_short', lang)}</div>
            </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
            <div class="stat-glass-box">
                <div class="stat-number">{len(appointments)}</div>
                <div class="stat-label">{t('card_appointments_short', lang)}</div>
            </div>
        """, unsafe_allow_html=True)

    # 5. "Still to take today" Glass Card
    st.markdown(f"""
        <div class="health-card" style="margin-top: 1.2rem;">
            <div style="font-size: 1.35rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.4rem;">{t('still_to_take_today', lang)}</div>
    """, unsafe_allow_html=True)

    pending_items = [x for x in today_schedule if x["status"] != "taken"]
    if not pending_items:
        st.markdown(f"""
            <div style="font-size: 1.15rem; font-weight: 600; color: #34D399; margin: 0.4rem 0;">
                {t('nothing_pending', lang)}
            </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("</div>", unsafe_allow_html=True)
        for item in pending_items:
            c_med_info, c_med_btn = st.columns([3, 2])
            with c_med_info:
                st.markdown(f"""
                    <div style="padding: 0.4rem 0;">
                        <b style="color: #FFFFFF; font-size: 1.15rem;">{item['medicine_name']}</b>
                        <span style="color: #94A3B8; margin-left: 0.4rem;">({item['dose']})</span>
                        <div style="font-size: 0.85rem; color: #06B6D4;">⏰ {t(item['slot'], lang)} &nbsp;|&nbsp; 🍽️ {item['food_instruction']}</div>
                    </div>
                """, unsafe_allow_html=True)
            with c_med_btn:
                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button(t("btn_taken", lang), key=f"d_tk_{item['medicine_id']}_{item['slot']}", use_container_width=True):
                        log_dose(parent_id, item['medicine_id'], item['slot'], today_str, "taken", user)
                        st.rerun()
                with cb2:
                    if st.button(t("btn_skip", lang), key=f"d_sk_{item['medicine_id']}_{item['slot']}", use_container_width=True):
                        log_dose(parent_id, item['medicine_id'], item['slot'], today_str, "skipped", user)
                        st.rerun()

    # 6. Call to Action Banner
    col_cta_text, col_cta_act = st.columns([5, 1])
    with col_cta_text:
        st.markdown(f"""
            <div class="cta-banner">
                <span>{t('cta_report_text', lang)}</span>
            </div>
        """, unsafe_allow_html=True)
    with col_cta_act:
        if st.button(t("cta_upload_btn", lang), key="cta_go_reports", use_container_width=True):
            st.session_state.current_page = "Medical Report Reader"
            st.rerun()

    # Safety advisory on missed doses
    safety_rule = MISSED_DOSE_SAFETY_RULE_TE if lang == "te" else MISSED_DOSE_SAFETY_RULE
    st.markdown(f'<div class="safety-alert" style="margin-top: 1rem;">{safety_rule}</div>', unsafe_allow_html=True)

    # Today's Medicine Tracker Quick Action Section
    st.markdown(f"### {t('today_medicine_tracker', lang)}")
    if not today_schedule:
        st.info(t("no_scheduled_meds", lang))
    else:
        # Group by slots: morning, afternoon, night
        for slot in ["morning", "afternoon", "night"]:
            slot_items = [x for x in today_schedule if x["slot"] == slot]
            if slot_items:
                slot_label = t(slot, lang)
                st.markdown(f"#### ⏰ {slot_label}")
                for item in slot_items:
                    card_col, act_col = st.columns([3, 2])
                    with card_col:
                        status_color = "#166534" if item["status"] == "taken" else "#991B1B" if item["status"] == "missed" else "#475569"
                        st.markdown(f"""
                            <div class="health-card" style="margin-bottom: 0.5rem; padding: 0.8rem 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <b style="font-size: 1.15rem; color: #FFFFFF;">{item['medicine_name']}</b>
                                        <span style="color: #94A3B8; margin-left: 0.5rem;">({item['dose']})</span>
                                        <div style="font-size: 0.85rem; color: #06B6D4; margin-top: 0.2rem;">🍽️ {item['food_instruction']}</div>
                                    </div>
                                    <span class="badge badge-{'normal' if item['status']=='taken' else 'urgent' if item['status']=='missed' else 'unknown'}">
                                        {item['status'].upper()}
                                    </span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    with act_col:
                        btn1, btn2, btn3 = st.columns(3)
                        with btn1:
                            if st.button(t("mark_taken", lang), key=f"t_{item['medicine_id']}_{slot}", use_container_width=True):
                                log_dose(parent_id, item['medicine_id'], slot, today_str, "taken", user)
                                st.rerun()
                        with btn2:
                            if st.button(t("mark_skipped", lang), key=f"s_{item['medicine_id']}_{slot}", use_container_width=True):
                                log_dose(parent_id, item['medicine_id'], slot, today_str, "skipped", user)
                                st.rerun()
                        with btn3:
                            if st.button(t("mark_missed", lang), key=f"m_{item['medicine_id']}_{slot}", use_container_width=True):
                                log_dose(parent_id, item['medicine_id'], slot, today_str, "missed", user)
                                st.rerun()

    st.markdown("---")

    # Historical Health Trends Chart
    st.markdown(f"### {t('trends_title', lang)}")
    st.caption(t("trends_caption", lang))

    # Extract test history across reports
    test_data = []
    for rep in reports:
        details = get_report_details(rep["id"], user)
        if details and "extracted_data" in details and "tests" in details["extracted_data"]:
            for t_item in details["extracted_data"]["tests"]:
                try:
                    num_val = float(''.join(c for c in str(t_item.get("value","")) if c.isdigit() or c=='.'))
                    test_data.append({
                        "Date": details["report_date"],
                        "Test": t_item.get("name", "Unknown"),
                        "Value": num_val,
                        "Unit": t_item.get("unit", "")
                    })
                except Exception:
                    pass

    if test_data:
        df_trends = pd.DataFrame(test_data)
        test_names = df_trends["Test"].unique()
        selected_test = st.selectbox(t("select_test_trend", lang), options=test_names)
        filtered_df = df_trends[df_trends["Test"] == selected_test].sort_values("Date")

        if len(filtered_df) > 0:
            fig = px.line(
                filtered_df,
                x="Date",
                y="Value",
                markers=True,
                title=f"{selected_test} Trend ({filtered_df['Unit'].iloc[0]})",
                labels={"Value": f"Level ({filtered_df['Unit'].iloc[0]})", "Date": "Report Date"}
            )
            fig.update_traces(line_color="#0D9488", line_width=3, marker=dict(size=10, color="#1E3A8A"))
            fig.update_layout(
                plot_bgcolor="#0A1626",
                paper_bgcolor="#0A1626",
                font_color="#F1F5F9",
                hovermode="x unified",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t("insufficient_trend_data", lang))
    else:
        st.info(t("no_lab_tests_trend", lang))


# ----------------- PAGE 2: MEDICAL REPORT READER -----------------
def render_report_reader(parent_id: int):
    user = st.session_state.user
    lang = st.session_state.preferred_lang

    if not parent_id:
        st.warning("Please connect to a parent account first.")
        return

    if not check_parent_access(user, parent_id):
        st.error("Unauthorized access to report reader.")
        return

    st.markdown(f"## {t('reader_title', lang)}")
    st.caption(t("reader_caption", lang))

    # Upload & Camera Input Tabs
    up_tab, cam_tab = st.tabs([t("tab_upload_file", lang), t("tab_camera", lang)])
    uploaded_file = None

    with up_tab:
        uploaded_file = st.file_uploader(
            t("uploader_label", lang),
            type=["pdf", "png", "jpg", "jpeg"]
        )

    with cam_tab:
        cam_file = st.camera_input(t("camera_label", lang))
        if cam_file:
            uploaded_file = cam_file

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        diff_opts = [t("diff_simple", lang), t("diff_detailed", lang)]
        diff_sel = st.selectbox(t("difficulty_label", lang), diff_opts, help=t("difficulty_help", lang))
        difficulty = "Simple" if diff_sel == t("diff_simple", lang) else "Detailed"
    with col_opt2:
        cat_opts = [t("cat_lab", lang), t("cat_rx", lang), t("cat_discharge", lang), t("cat_consult", lang)]
        report_type = st.selectbox(t("category_label", lang), cat_opts)

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name

        # Process and validate
        valid, err_msg, images_list = process_uploaded_document_to_images(file_name, file_bytes)

        if not valid:
            st.error(f"❌ Document Validation Failed: {err_msg}")
        else:
            st.success(f"✅ Document successfully loaded ({len(images_list)} page(s) ready for analysis).")

            # Document preview expander
            with st.expander(t("preview_expander", lang), expanded=False):
                p_cols = st.columns(min(len(images_list), 3))
                for idx, img in enumerate(images_list[:3]):
                    with p_cols[idx]:
                        st.image(img, caption=f"{t('page_caption', lang)} {idx + 1}", use_container_width=True)

            if st.button(t("btn_analyze", lang), type="primary", use_container_width=True):
                with st.spinner(t("spinner_analyzing", lang)):
                    # Call Claude AI Service (with automatic demo fallback)
                    analysis = analyze_medical_document(
                        image_bytes_list=images_list,
                        mime_type="image/png",
                        language=lang,
                        difficulty=difficulty
                    )
                    st.session_state["current_analysis"] = analysis
                    st.session_state["current_file_bytes"] = file_bytes
                    st.session_state["current_file_name"] = file_name
                    st.session_state["current_report_type"] = report_type

    # Render Review and Correction Screen if analysis is available
    if "current_analysis" in st.session_state:
        analysis: ReportExplanation = st.session_state["current_analysis"]
        st.markdown("---")
        st.markdown(f"### {t('review_title', lang)}")
        st.caption(t("review_caption", lang))

        if analysis.is_demo:
            st.warning(t("demo_mode_badge", lang))

        # Audio Explanation Option
        st.markdown(f"#### {t('summary_heading', lang)}")
        st.markdown(f"""
            <div class="health-card" style="background-color: rgba(13, 27, 46, 0.72); border-left: 5px solid #06B6D4;">
                <p style="font-size: 1.1rem; line-height: 1.6; color: #FFFFFF;">{analysis.summary}</p>
            </div>
        """, unsafe_allow_html=True)

        # Audio TTS Player
        if st.button(t("listen_audio", lang)):
            with st.spinner(t("audio_spinner", lang)):
                audio_bytes = generate_tts_audio(analysis.summary, lang=lang)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.warning(t("audio_offline_warning", lang))

        # Editable Extracted Tests Table
        st.markdown(f"#### {t('tests_heading', lang)}")
        tests_data = [t_item.model_dump() for t_item in analysis.tests]
        if tests_data:
            df_tests = pd.DataFrame(tests_data)
            edited_tests_df = st.data_editor(
                df_tests,
                column_config={
                    "name": st.column_config.TextColumn("Test Name", required=True),
                    "value": st.column_config.TextColumn("Observed Value", required=True),
                    "unit": st.column_config.TextColumn("Unit"),
                    "reference_range": st.column_config.TextColumn("Reference Range"),
                    "status": st.column_config.SelectboxColumn("Status", options=["normal", "watch", "urgent", "unknown"]),
                    "meaning": st.column_config.TextColumn("Meaning / Explanation"),
                    "confidence_or_uncertainty": st.column_config.TextColumn("Confidence / OCR Note")
                },
                use_container_width=True,
                num_rows="dynamic",
                key="editor_tests"
            )
        else:
            st.info(t("no_tests_detected", lang))
            edited_tests_df = pd.DataFrame()

        # Editable Extracted Medicines Table
        st.markdown(f"#### {t('meds_heading', lang)}")
        meds_data = [m.model_dump() for m in analysis.medicines]
        if meds_data:
            df_meds = pd.DataFrame(meds_data)
            edited_meds_df = st.data_editor(
                df_meds,
                column_config={
                    "name": st.column_config.TextColumn("Medicine Name", required=True),
                    "dose": st.column_config.TextColumn("Dose"),
                    "frequency": st.column_config.TextColumn("Frequency"),
                    "timing": st.column_config.TextColumn("Timing Slots"),
                    "food_instruction": st.column_config.SelectboxColumn("Food Instruction", options=["Before Food", "After Food", "With Food", "Empty Stomach"]),
                    "duration": st.column_config.TextColumn("Duration")
                },
                use_container_width=True,
                num_rows="dynamic",
                key="editor_meds"
            )
        else:
            st.info(t("no_meds_detected", lang))
            edited_meds_df = pd.DataFrame()

        # Questions to Ask Your Doctor & Diet Tips
        c_q, c_t = st.columns(2)
        with c_q:
            st.markdown(f"#### {t('doctor_questions_heading', lang)}")
            for q in analysis.doctor_questions:
                st.markdown(f"- **{q}**")
        with c_t:
            st.markdown(f"#### {t('diet_tips_heading', lang)}")
            for tip in analysis.food_tips:
                st.markdown(f"- {tip}")

        # Mandatory Medical Disclaimer
        disclaimer_text = MANDATORY_DISCLAIMER_TE if lang == "te" else MANDATORY_DISCLAIMER
        st.markdown(f"""
            <div class="disclaimer-box">
                <b>⚖️ DISCLAIMER:</b> {disclaimer_text}
            </div>
        """, unsafe_allow_html=True)

        # Action: Save Confirmed Report to History
        st.markdown(f"#### {t('save_doc_heading', lang)}")
        save_col1, save_col2 = st.columns([2, 1])
        with save_col1:
            report_title = st.text_input(t("report_title_label", lang), value=f"{st.session_state['current_report_type']} - {date.today().strftime('%b %Y')}")
            rep_date = st.date_input(t("report_date_label", lang), value=date.today())
            doc_name = st.text_input(t("doctor_name_label", lang), value=analysis.doctor_name or "")
            fac_name = st.text_input(t("facility_label", lang), value=analysis.facility_name or "")

        with save_col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button(t("btn_save_report", lang), type="primary", use_container_width=True):
                from security import save_uploaded_file_securely
                file_bytes = st.session_state["current_file_bytes"]
                file_name = st.session_state["current_file_name"]

                saved_path, file_hash = save_uploaded_file_securely(file_name, file_bytes)

                final_tests = edited_tests_df.to_dict(orient="records") if not edited_tests_df.empty else []
                final_meds = edited_meds_df.to_dict(orient="records") if not edited_meds_df.empty else []

                extracted_data = {
                    "tests": final_tests,
                    "medicines": final_meds,
                    "doctor_questions": analysis.doctor_questions,
                    "food_tips": analysis.food_tips,
                    "is_demo": analysis.is_demo
                }
                explanation = {
                    "summary": analysis.summary,
                    "doctor_questions": analysis.doctor_questions,
                    "food_tips": analysis.food_tips,
                    "disclaimer": analysis.disclaimer
                }

                rep_id = save_medical_report(
                    user_id=parent_id,
                    title=report_title,
                    report_date=rep_date.isoformat(),
                    doctor_name=doc_name,
                    facility_name=fac_name,
                    report_type=st.session_state["current_report_type"],
                    file_path=saved_path,
                    file_hash=file_hash,
                    extracted_data=extracted_data,
                    explanation=explanation,
                    actor_id=user["id"]
                )

                # Option: also auto-schedule medicines if user confirms
                if final_meds:
                    for m in final_meds:
                        t_slot = ["morning"]
                        if "night" in str(m.get("timing","")).lower():
                            t_slot.append("night")
                        add_medicine(
                            user_id=parent_id,
                            name=m.get("name", "Prescribed Med"),
                            dose=m.get("dose", ""),
                            frequency=m.get("frequency", "Once daily"),
                            timing_slots=t_slot,
                            food_instruction=m.get("food_instruction", "After Food"),
                            duration=m.get("duration", ""),
                            actor_id=user["id"]
                        )

                st.success(t("report_saved_success", lang))
                del st.session_state["current_analysis"]
                st.rerun()

# ----------------- PAGE 3: MEDICINE MANAGER -----------------
def render_medicine_manager(parent_id: int):
    user = st.session_state.user
    lang = st.session_state.preferred_lang

    if not parent_id:
        st.warning("Please connect to a parent account first.")
        return

    if not check_parent_access(user, parent_id):
        st.error("Unauthorized access to medicine manager.")
        return

    st.markdown(f"## {t('med_mgr_title', lang)}")
    st.caption(t("med_mgr_caption", lang))

    # Missed dose warning rule
    safety_rule = MISSED_DOSE_SAFETY_RULE_TE if lang == "te" else MISSED_DOSE_SAFETY_RULE
    st.markdown(f'<div class="safety-alert">{safety_rule}</div>', unsafe_allow_html=True)

    tab_sched, tab_log, tab_analytics = st.tabs([
        t("tab_med_sched", lang),
        t("tab_dose_log", lang),
        t("tab_analytics", lang)
    ])

    # TAB 1: Schedules (Add, Edit, Deactivate, Delete)
    with tab_sched:
        st.markdown(f"### {t('active_meds_heading', lang)}")
        medicines = get_user_medicines(parent_id, user, active_only=False)

        if not medicines:
            st.info(t("no_meds_registered", lang))
        else:
            for med in medicines:
                status_badge = "badge-normal" if med["is_active"] else "badge-unknown"
                status_text = t("badge_active", lang) if med["is_active"] else t("badge_inactive", lang)
                slots_str = ", ".join([t(s.lower(), lang) if s.lower() in ["morning", "afternoon", "night"] else s.capitalize() for s in med["timing_slots"]])

                with st.container():
                    st.markdown(f"""
                        <div class="health-card" style="padding: 1rem 1.25rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h4 style="margin: 0; font-size: 1.2rem; color: #FFFFFF;">{med['name']} <span style="font-size: 0.95rem; color: #94A3B8;">({med['dose']})</span></h4>
                                    <div style="font-size: 0.9rem; color: #E2E8F0; margin-top: 0.25rem;">
                                        ⏰ <b>{t('label_timing', lang)}:</b> {slots_str} &nbsp;|&nbsp; 🍽️ <b>{t('label_food', lang)}:</b> {med['food_instruction']} &nbsp;|&nbsp; ⏳ <b>{t('label_duration', lang)}:</b> {med['duration'] or t('label_ongoing', lang)}
                                    </div>
                                </div>
                                <span class="badge {status_badge}">{status_text}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    c_act1, c_act2, c_act3 = st.columns([1, 1, 4])
                    with c_act1:
                        toggle_label = t("btn_deactivate", lang) if med["is_active"] else t("btn_activate", lang)
                        if st.button(toggle_label, key=f"tog_{med['id']}"):
                            update_medicine(
                                med_id=med["id"],
                                name=med["name"],
                                dose=med["dose"],
                                frequency=med["frequency"],
                                timing_slots=med["timing_slots"],
                                food_instruction=med["food_instruction"],
                                duration=med["duration"],
                                is_active=not med["is_active"],
                                current_user=user
                            )
                            st.rerun()
                    with c_act2:
                        if st.button(t("btn_delete", lang), key=f"del_{med['id']}"):
                            delete_medicine(med["id"], user)
                            st.rerun()

        st.markdown("---")
        st.markdown(f"### {t('add_med_heading', lang)}")
        with st.form("add_med_form"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                new_name = st.text_input(t("med_name_label", lang), placeholder="e.g. Metformin")
                new_dose = st.text_input(t("med_dose_label", lang), placeholder="e.g. 500 mg")
                new_freq = st.selectbox(t("freq_label", lang), ["Once daily", "Twice daily", "Three times daily", "As needed"])
            with col_m2:
                st.markdown(f"**{t('timing_slots_label', lang)}**")
                slot_m = st.checkbox(t("slot_morning_ist", lang), value=True)
                slot_a = st.checkbox(t("slot_afternoon_ist", lang))
                slot_n = st.checkbox(t("slot_night_ist", lang))
                new_food = st.selectbox(t("food_instructions_label", lang), [t("food_after", lang), t("food_before", lang), t("food_with", lang), t("food_empty", lang)])
                new_dur = st.text_input(t("duration_label", lang), placeholder="e.g. 30 days, Ongoing")

            add_sub = st.form_submit_button(t("btn_add_med_submit", lang), type="primary", use_container_width=True)
            if add_sub:
                if not new_name or not new_dose:
                    st.error(t("err_enter_med_dose", lang))
                else:
                    slots = []
                    if slot_m: slots.append("morning")
                    if slot_a: slots.append("afternoon")
                    if slot_n: slots.append("night")
                    if not slots:
                        st.error(t("err_select_timing_slot", lang))
                    else:
                        add_medicine(
                            user_id=parent_id,
                            name=new_name,
                            dose=new_dose,
                            frequency=new_freq,
                            timing_slots=slots,
                            food_instruction=new_food,
                            duration=new_dur,
                            actor_id=user["id"]
                        )
                        st.success(t("success_added_med", lang, name=new_name))
                        st.rerun()

    # TAB 2: Daily Dose Log
    with tab_log:
        st.markdown(f"### {t('tab_dose_log', lang)}")
        selected_log_date = st.date_input(t("select_log_date", lang), value=date.today())
        date_str = selected_log_date.isoformat()

        daily_items = get_daily_schedule_with_logs(parent_id, date_str, user)
        if not daily_items:
            st.info(t("no_meds_for_date", lang, date=date_str))
        else:
            for item in daily_items:
                col_i1, col_i2 = st.columns([3, 2])
                with col_i1:
                    st.markdown(f"""
                        <div class="health-card" style="margin-bottom: 0.5rem;">
                            <b>{item['medicine_name']}</b> ({item['dose']}) — <i>{t(item['slot'], lang)}</i><br/>
                            <span style="font-size: 0.85rem; color: #94A3B8;">Status: <b>{item['status'].upper()}</b> {f'(Logged: {item["logged_at"]})' if item['logged_at'] else ''}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with col_i2:
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button(t("btn_taken", lang), key=f"dlg_t_{item['medicine_id']}_{item['slot']}", use_container_width=True):
                            log_dose(parent_id, item['medicine_id'], item['slot'], date_str, "taken", user)
                            st.rerun()
                    with b2:
                        if st.button(t("btn_skipped", lang), key=f"dlg_s_{item['medicine_id']}_{item['slot']}", use_container_width=True):
                            log_dose(parent_id, item['medicine_id'], item['slot'], date_str, "skipped", user)
                            st.rerun()
                    with b3:
                        if st.button(t("btn_missed", lang), key=f"dlg_m_{item['medicine_id']}_{item['slot']}", use_container_width=True):
                            log_dose(parent_id, item['medicine_id'], item['slot'], date_str, "missed", user)
                            st.rerun()

    # TAB 3: Analytics
    with tab_analytics:
        st.markdown(f"### {t('tab_analytics', lang)}")
        adherence_7 = get_adherence_stats(parent_id, days=7, current_user=user)
        adherence_30 = get_adherence_stats(parent_id, days=30, current_user=user)

        c_a1, c_a2 = st.columns(2)
        with c_a1:
            st.markdown(f"""
                <div class="stat-glass-box">
                    <div class="stat-label">{t('adherence_7day', lang)}</div>
                    <div class="stat-number">{adherence_7['adherence_rate']}%</div>
                    <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 0.3rem;">{t('adherence_sub', lang, taken=adherence_7['taken'], skipped=adherence_7['skipped'], missed=adherence_7['missed'])}</div>
                </div>
            """, unsafe_allow_html=True)
        with c_a2:
            st.markdown(f"""
                <div class="stat-glass-box">
                    <div class="stat-label">{t('adherence_30day', lang)}</div>
                    <div class="stat-number">{adherence_30['adherence_rate']}%</div>
                    <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 0.3rem;">{t('adherence_sub', lang, taken=adherence_30['taken'], skipped=adherence_30['skipped'], missed=adherence_30['missed'])}</div>
                </div>
            """, unsafe_allow_html=True)

        # Plotly Adherence Donut Chart
        if adherence_30["total"] > 0:
            fig = px.pie(
                values=[adherence_30["taken"], adherence_30["skipped"], adherence_30["missed"]],
                names=[t("btn_taken", lang), t("btn_skipped", lang), t("btn_missed", lang)],
                color=[t("btn_taken", lang), t("btn_skipped", lang), t("btn_missed", lang)],
                color_discrete_map={t("btn_taken", lang): "#10B981", t("btn_skipped", lang): "#F59E0B", t("btn_missed", lang): "#EF4444"},
                hole=0.45,
                title=t("chart_adherence_title", lang)
            )
            fig.update_layout(
                plot_bgcolor="#0A1626",
                paper_bgcolor="#0A1626",
                font_color="#F1F5F9",
                margin=dict(t=40, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

# ----------------- PAGE 4: APPOINTMENT MANAGER -----------------
def render_appointment_manager(parent_id: int):
    user = st.session_state.user
    lang = st.session_state.preferred_lang

    if not parent_id:
        st.warning(t("dashboard_connect_parent_warning", lang))
        return

    if not check_parent_access(user, parent_id):
        st.error(t("dashboard_access_denied", lang))
        return

    st.markdown(f"## {t('app_mgr_title', lang)}")
    st.caption(t("app_mgr_caption", lang))

    app_tab1, app_tab2 = st.tabs([t("tab_app_list", lang), t("tab_app_new", lang)])

    with app_tab1:
        appointments = get_user_appointments(parent_id, user)
        if not appointments:
            st.info(t("no_app_scheduled", lang))
        else:
            for app in appointments:
                is_upcoming = app["status"] == "upcoming"
                badge_class = "badge-normal" if app["status"] == "completed" else "badge-watch" if is_upcoming else "badge-unknown"

                st.markdown(f"""
                    <div class="health-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h4 style="margin: 0; color: #FFFFFF; font-size: 1.2rem;">👨‍⚕️ {app['doctor_name']}</h4>
                                <div style="color: #94A3B8; font-size: 0.95rem; margin-top: 0.2rem;">
                                    🏥 <b>{t('app_location', lang)}:</b> {app['facility']} &nbsp;|&nbsp; 📍 <b>{t('app_mode', lang)}:</b> {app['mode']}
                                </div>
                                <div style="color: #06B6D4; font-size: 0.95rem; margin-top: 0.2rem; font-weight: 600;">
                                    📅 <b>{t('app_date', lang)}:</b> {app['appointment_date']} at {app['appointment_time']} &nbsp;|&nbsp; 📞 {app['contact_number'] or 'N/A'}
                                </div>
                                {f'<div style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.3rem;">📝 <i>{t("app_notes", lang)}: {app["notes"]}</i></div>' if app["notes"] else ''}
                            </div>
                            <span class="badge {badge_class}">{app['status'].upper()}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_upcoming:
                    c1, c2, c3 = st.columns([1, 1, 4])
                    with c1:
                        if st.button(t("btn_mark_completed", lang), key=f"cmp_{app['id']}"):
                            update_appointment_status(app["id"], "completed", user)
                            st.rerun()
                    with c2:
                        if st.button(t("btn_cancel_visit", lang), key=f"cnc_{app['id']}"):
                            cancel_appointment(app["id"], user)
                            st.rerun()

    with app_tab2:
        st.markdown(f"### {t('tab_app_new', lang)}")
        with st.form("new_app_form"):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                doc_name = st.text_input(t("doc_name_spec_label", lang), placeholder="e.g. Dr. S. K. Sharma (Cardiology)")
                facility = st.text_input(t("clinic_label", lang), placeholder="e.g. Apollo Hospital, Jubilee Hills")
                mode_opts = [t("mode_in_person", lang), t("mode_video", lang), t("mode_phone", lang)]
                app_mode = st.selectbox(t("consult_mode_label", lang), mode_opts)
            with col_a2:
                app_date = st.date_input(t("app_date_label", lang), value=date.today() + timedelta(days=2))
                app_time = st.time_input(t("app_time_label", lang), value=datetime.strptime("10:30", "%H:%M").time())
                app_phone = st.text_input(t("clinic_phone_label", lang), placeholder="+91 98765 00000")

            app_notes = st.text_area(t("notes_purpose_label", lang), placeholder="Routine blood pressure checkup, discuss lipid profile...")

            app_sub = st.form_submit_button(t("btn_schedule_submit", lang), type="primary", use_container_width=True)
            if app_sub:
                if not doc_name or not facility:
                    st.error(t("err_doc_clinic_req", lang))
                else:
                    time_str = app_time.strftime("%H:%M")
                    add_appointment(
                        user_id=parent_id,
                        doctor_name=doc_name,
                        facility=facility,
                        appointment_date=app_date.isoformat(),
                        appointment_time=time_str,
                        contact_number=app_phone,
                        mode=app_mode,
                        notes=app_notes,
                        current_user=user
                    )
                    st.success(t("success_app_scheduled", lang, doctor=doc_name))
                    st.rerun()

# ----------------- PAGE 5: HEALTH HISTORY & MONTHLY PDF -----------------
def render_health_history(parent_id: int):
    user = st.session_state.user
    lang = st.session_state.preferred_lang

    if not parent_id:
        st.warning(t("dashboard_connect_parent_warning", lang))
        return

    if not check_parent_access(user, parent_id):
        st.error(t("dashboard_access_denied", lang))
        return

    st.markdown(f"## {t('hist_title', lang)}")
    st.caption(t("hist_caption", lang))

    hist_tab1, hist_tab2 = st.tabs([t("tab_hist_archive", lang), t("tab_hist_pdf", lang)])

    with hist_tab1:
        reports = get_user_reports(parent_id, user)
        if not reports:
            st.info(t("no_reports_saved", lang))
        else:
            search_query = st.text_input(t("search_reports_placeholder", lang), "").lower()
            filtered_reports = [r for r in reports if search_query in r["title"].lower() or search_query in (r["doctor_name"] or "").lower()]

            for rep in filtered_reports:
                with st.expander(f"📄 {rep['report_date']} — {rep['title']} ({rep['report_type']})", expanded=False):
                    details = get_report_details(rep["id"], user)
                    if details:
                        st.markdown(f"**{t('facility_label', lang)}:** {details.get('facility_name', 'N/A')} &nbsp;|&nbsp; **{t('doctor_name_label', lang)}:** {details.get('doctor_name', 'N/A')}")

                        if "explanation" in details and "summary" in details["explanation"]:
                            st.markdown(f"""
                                <div class="health-card" style="background-color: rgba(13, 27, 46, 0.72);">
                                    <b>{t('summary_heading', lang)}:</b><br/>{details['explanation']['summary']}
                                </div>
                            """, unsafe_allow_html=True)

                            if st.button(t("listen_audio", lang), key=f"aud_{rep['id']}"):
                                audio_bytes = generate_tts_audio(details['explanation']['summary'], lang=lang)
                                if audio_bytes:
                                    st.audio(audio_bytes, format="audio/mp3")

                        if "extracted_data" in details and "tests" in details["extracted_data"]:
                            tests = details["extracted_data"]["tests"]
                            if tests:
                                st.markdown(f"##### {t('tests_heading', lang)}")
                                st.dataframe(pd.DataFrame(tests), use_container_width=True)

                        if st.button(t("btn_delete_report", lang), key=f"del_rep_{rep['id']}"):
                            delete_medical_report(rep["id"], user)
                            st.success(t("report_deleted_msg", lang))
                            st.rerun()

    with hist_tab2:
        st.markdown(f"### {t('pdf_gen_heading', lang)}")
        st.caption(t("pdf_gen_caption", lang))

        current_year = date.today().year
        selected_year = st.selectbox(t("year_label", lang), [current_year, current_year - 1], index=0)
        selected_month = st.selectbox(t("month_label", lang), [f"{m:02d}" for m in range(1, 13)], index=date.today().month - 1)
        target_month_year = f"{selected_year}-{selected_month}"

        if st.button(t("btn_generate_pdf", lang), type="primary", use_container_width=True):
            with st.spinner(t("spinner_compiling_pdf", lang)):
                pdf_path = generate_monthly_health_summary_pdf(parent_id, target_month_year, user)
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()

                    st.success(t("pdf_success_msg", lang))
                    st.download_button(
                        label=t("btn_download_pdf_file", lang),
                        data=pdf_bytes,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error(t("pdf_failed_msg", lang))

# ----------------- PAGE 6: FAMILY CONNECTIONS -----------------
def render_family_connections():
    user = st.session_state.user
    lang = st.session_state.preferred_lang

    st.markdown(f"## {t('fam_title', lang)}")
    st.caption(t("fam_caption", lang))

    if user["role"] == "parent":
        st.markdown(f"### {t('fam_parent_portal', lang)}")

        c_inv1, c_inv2 = st.columns([2, 1])
        with c_inv1:
            st.markdown(t("fam_parent_desc", lang))
        with c_inv2:
            rel_options = [t("rel_son", lang), t("rel_daughter", lang), t("rel_spouse", lang), t("rel_caregiver", lang)]
            rel_label = st.selectbox(t("fam_relation_label", lang), rel_options)
            if st.button(t("btn_gen_invite", lang), type="primary", use_container_width=True):
                code = generate_invite_code(user["id"], relationship=rel_label)
                st.success(f"Generated Invitation Code: **{code}**\n\nShare this code with your {rel_label}.")

        st.markdown("---")
        st.markdown(f"### {t('fam_members_heading', lang)}")
        members = get_parent_family_members(user["id"])

        if not members:
            st.info(t("no_invite_codes", lang))
        else:
            for m in members:
                status_color = "badge-normal" if m["status"] == "approved" else "badge-urgent" if m["status"] == "revoked" else "badge-watch"
                with st.container():
                    st.markdown(f"""
                        <div class="health-card" style="padding: 1rem 1.25rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <b style="font-size: 1.15rem; color: #FFFFFF;">{m['child_name'] or 'Invitation Pending'}</b>
                                    <span style="color: #94A3B8; margin-left: 0.5rem;">({m['relationship']})</span>
                                    <div style="font-size: 0.85rem; color: #E2E8F0; margin-top: 0.2rem;">
                                        Code: <code style="background: rgba(13, 27, 46, 0.9); padding: 2px 6px; border-radius: 4px; color: #06B6D4;">{m['invite_code']}</code> &nbsp;|&nbsp;
                                        Email: {m['child_email'] or 'Not claimed yet'} &nbsp;|&nbsp;
                                        Created: {m['created_at']}
                                    </div>
                                </div>
                                <span class="badge {status_color}">{m['status'].upper()}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    if m["child_user_id"] and m["status"] == "pending":
                        c_app, c_rev = st.columns([1, 1])
                        with c_app:
                            if st.button(t("btn_approve_access", lang), key=f"app_{m['id']}"):
                                update_link_status(m["id"], user, "approved")
                                st.rerun()
                        with c_rev:
                            if st.button(t("btn_reject_request", lang), key=f"rej_{m['id']}"):
                                update_link_status(m["id"], user, "revoked")
                                st.rerun()
                    elif m["child_user_id"] and m["status"] == "approved":
                        if st.button(t("btn_revoke_access", lang), key=f"rev_{m['id']}"):
                            update_link_status(m["id"], user, "revoked")
                            st.rerun()

    else:
        # Child Portal
        st.markdown(f"### {t('fam_child_portal', lang)}")
        st.markdown(t("fam_child_desc", lang))

        with st.form("child_connect_form"):
            code_input = st.text_input(t("invite_code_label", lang), placeholder="e.g. HB-WELCOME or HB-A1B2C3").strip().upper()
            sub = st.form_submit_button(t("btn_request_connect", lang), type="primary", use_container_width=True)

            if sub:
                if not code_input:
                    st.error(t("err_enter_invite_code", lang))
                else:
                    success, msg = connect_with_invite_code(user, code_input)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown("---")
        st.markdown(f"### {t('connected_parents_heading', lang)}")
        parents = get_child_connected_parents(user["id"])
        if not parents:
            st.info(t("no_connected_parents", lang))
        else:
            for p in parents:
                st.markdown(f"""
                    <div class="health-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: #FFFFFF;">👴 {p['parent_name']}</h4>
                                <div style="color: #94A3B8; font-size: 0.9rem; margin-top: 0.2rem;">
                                    {t('fam_relation_label', lang)}: <b>{p['relationship']}</b> &nbsp;|&nbsp; {p['approved_at']} &nbsp;|&nbsp; {p['parent_email']}
                                </div>
                            </div>
                            <span class="badge badge-normal">{t('badge_connected', lang)}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# ----------------- PAGE 7: SETTINGS -----------------
def render_settings():
    user = st.session_state.user
    lang = st.session_state.preferred_lang

    st.markdown(f"## {t('settings_title', lang)}")
    st.caption(t("settings_caption", lang))

    set_tab1, set_tab2, set_tab3 = st.tabs([
        t("tab_set_profile", lang),
        t("tab_set_telegram", lang),
        t("tab_set_privacy", lang)
    ])

    with set_tab1:
        st.markdown(f"### {t('user_profile_heading', lang)}")
        with st.form("profile_form"):
            p_name = st.text_input(t("full_name_label", lang), value=user["full_name"])
            p_phone = st.text_input(t("phone_label", lang), value=user["phone"] or "")
            p_lang = st.selectbox(
                t("preferred_lang_label", lang),
                options=list(config.SUPPORTED_LANGUAGES.keys()),
                format_func=lambda x: config.SUPPORTED_LANGUAGES[x],
                index=list(config.SUPPORTED_LANGUAGES.keys()).index(user["preferred_lang"]) if user["preferred_lang"] in config.SUPPORTED_LANGUAGES else 0
            )
            p_tg = st.text_input(t("tg_chat_id_label", lang), value=user.get("telegram_chat_id") or "", help=t("tg_chat_id_help", lang))

            st.markdown(f"**{t('notif_prefs_heading', lang)}**")
            notif_med = st.checkbox(t("notif_med_reminders", lang), value=bool(user.get("notify_medicines", 1)))
            notif_app = st.checkbox(t("notif_app_reminders", lang), value=bool(user.get("notify_appointments", 1)))

            p_submit = st.form_submit_button(t("btn_save_profile", lang), type="primary", use_container_width=True)
            if p_submit:
                update_user_profile(
                    user_id=user["id"],
                    full_name=p_name,
                    phone=p_phone,
                    preferred_lang=p_lang,
                    telegram_chat_id=p_tg,
                    notify_medicines=notif_med,
                    notify_appointments=notif_app
                )
                st.session_state.user = get_user_by_id(user["id"])
                st.session_state.preferred_lang = p_lang
                st.query_params["lang"] = p_lang
                st.success(t("profile_updated_success", lang))
                st.rerun()

    with set_tab2:
        st.markdown(f"### {t('tg_integration_heading', lang)}")
        st.markdown(t("tg_integration_desc", lang))

        tg_id = user.get("telegram_chat_id")
        if not tg_id:
            st.info(t("tg_enable_hint", lang))
        else:
            st.success(f"{t('tg_id_configured', lang)}: `{tg_id}`")
            if st.button(t("btn_test_tg", lang), use_container_width=True):
                with st.spinner(t("tg_dispatch_spinner", lang)):
                    success, msg = send_test_telegram_ping(tg_id, user["id"])
                    if success:
                        st.success(t("tg_ping_success", lang))
                    else:
                        st.warning(f"Delivery notice: {msg}")

    with set_tab3:
        st.markdown(f"### {t('privacy_heading', lang)}")
        st.markdown(t("privacy_bullets", lang))

# ----------------- BOTTOM FLOATING DOCK NAVIGATION -----------------
def render_bottom_dock():
    lang = st.session_state.preferred_lang

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 0.6rem;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #06B6D4; letter-spacing: 0.08em; text-transform: uppercase;">
                {t('nav_dock_label', lang)}
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    _, dock_center, _ = st.columns([1, 8, 1])
    with dock_center:
        d1, d2, d3, d4, d5 = st.columns(5)
        with d1:
            if st.button(f"🏠 {t('nav_dashboard', lang)}", key="dock_btn_home", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
        with d2:
            if st.button(f"📄 {t('nav_reports', lang)}", key="dock_btn_reports", use_container_width=True):
                st.session_state.current_page = "Medical Report Reader"
                st.rerun()
        with d3:
            if st.button(f"💊 {t('nav_medicines', lang)}", key="dock_btn_meds", use_container_width=True):
                st.session_state.current_page = "Medicine Manager"
                st.rerun()
        with d4:
            if st.button(f"🎙️ {t('nav_ask', lang)}", key="dock_btn_ask", use_container_width=True):
                st.session_state.current_page = "Medical Report Reader"
                st.rerun()
        with d5:
            if st.button(f"☰ {t('nav_more', lang)}", key="dock_btn_more", use_container_width=True):
                st.session_state.current_page = "More"
                st.rerun()

# ----------------- FOOTER -----------------
def render_footer():
    lang = st.session_state.preferred_lang
    st.markdown(f"""
        <div style="margin-top: 3.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(20, 184, 166, 0.2); text-align: center; color: #64748B; font-size: 0.88rem; line-height: 1.6;">
            <p style="margin-bottom: 0.4rem; color: #94A3B8; font-weight: 600;">{t('footer_rights', lang)}</p>
            <p style="font-size: 0.82rem; color: #64748B; max-width: 720px; margin: auto;">{t('footer_disclaimer', lang)}</p>
        </div>
    """, unsafe_allow_html=True)

# ----------------- MAIN APP ROUTING -----------------
def main():
    if not st.session_state.user:
        render_auth_view()
        render_footer()
    else:
        render_top_navbar()
        page = st.session_state.current_page
        parent_id = st.session_state.active_parent_id

        if page == "Dashboard":
            render_dashboard(parent_id)
        elif page == "Medical Report Reader":
            render_report_reader(parent_id)
        elif page == "Medicine Manager":
            render_medicine_manager(parent_id)
        elif page == "Appointment Manager":
            render_appointment_manager(parent_id)
        elif page == "Health History":
            render_health_history(parent_id)
        elif page == "Family Connections":
            render_family_connections()
        elif page == "Settings":
            render_settings()
        elif page == "More":
            render_more_hub(parent_id)

        render_bottom_dock()
        render_footer()

if __name__ == "__main__":
    main()


