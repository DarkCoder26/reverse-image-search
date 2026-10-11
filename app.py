# -\*- coding: utf-8 -\*-

"""

Reverse Image Search — Cyber-themed production entry point.

Run with:

    streamlit run app.py

"""

import logging

import streamlit as st

from components.privacy_policy import render_privacy_policy

from config.settings import (

    ALLOWED_EXTENSIONS,

    MAX_IMAGE_SIZE_MB,

)

from services.search_engine import run_search

from utils.validators import validate_image, ValidationError

from utils.rate_limiter import check_rate_limit, get_remaining_quota

from components.results_view import render_analysis, render_results

from components.terms import render_terms_gate

# ------------------------------------------------------------------

# Logging

# ------------------------------------------------------------------

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",

)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------

# Page config — MUST be the first Streamlit command

# ------------------------------------------------------------------

st.set_page_config(

    page_title="OSINT :: Reverse Image Search",

    page_icon="🛰️",

    layout="wide",

    initial_sidebar_state="expanded",

)

# ------------------------------------------------------------------

# Cyber theme CSS

# ------------------------------------------------------------------

CYBER_CSS = """

<style>

html, body, [class*="css"] {

    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;

}

.stApp {

    background:

        radial-gradient(circle at 20% 0%, rgba(0, 255, 170, 0.06), transparent 40%),

        radial-gradient(circle at 80% 100%, rgba(0, 180, 255, 0.06), transparent 40%),

        #060a08;

    color: #c8f7e4;

}

.stApp::before {

    content: "";

    position: fixed;

    inset: 0;

    background-image:

        linear-gradient(rgba(0, 255, 170, 0.03) 1px, transparent 1px),

        linear-gradient(90deg, rgba(0, 255, 170, 0.03) 1px, transparent 1px);

    background-size: 40px 40px;

    pointer-events: none;

    z-index: 0;

}

h1, h2, h3, h4 {

    color: #00ffaa !important;

    letter-spacing: 0.5px;

    text-shadow: 0 0 8px rgba(0, 255, 170, 0.35);

}

section[data-testid="stSidebar"] {

    background: linear-gradient(180deg, #071410 0%, #04100c 100%);

    border-right: 1px solid rgba(0, 255, 170, 0.25);

}

section[data-testid="stSidebar"] * {

    color: #aef7d4 !important;

}

.stButton > button {

    background: linear-gradient(135deg, #00ffaa 0%, #00cc88 100%);

    color: #04110c !important;

    font-weight: 700;

    letter-spacing: 1px;

    border: none;

    border-radius: 6px;

    padding: 0.6rem 1rem;

    transition: all 0.2s ease;

}

.stButton > button:hover {

    transform: translateY(-1px);

    box-shadow: 0 0 24px rgba(0, 255, 170, 0.55);

}

.stButton > button:disabled {

    background: rgba(0, 255, 170, 0.15);

    color: #5fa88e !important;

    box-shadow: none;

}

section[data-testid="stFileUploaderDropzone"] {

    background: rgba(0, 255, 170, 0.03) !important;

    border: 1.5px dashed rgba(0, 255, 170, 0.45) !important;

    border-radius: 10px !important;

    transition: all 0.2s ease;

}

section[data-testid="stFileUploaderDropzone"]:hover {

    background: rgba(0, 255, 170, 0.06) !important;

    border-color: #00ffaa !important;

    box-shadow: 0 0 22px rgba(0, 255, 170, 0.25) inset;

}

div[data-testid="stMetric"] {

    background: rgba(0, 255, 170, 0.05);

    border: 1px solid rgba(0, 255, 170, 0.25);

    border-radius: 8px;

    padding: 10px 14px;

}

div[data-testid="stMetricValue"] {

    color: #00ffaa !important;

}

.stProgress > div > div > div > div {

    background: linear-gradient(90deg, #00ffaa, #00d0ff) !important;

}

div[data-testid="stVerticalBlockBorderWrapper"] {

    background: rgba(4, 20, 16, 0.6);

    border: 1px solid rgba(0, 255, 170, 0.20) !important;

    border-radius: 10px !important;

    transition: all 0.15s ease;

}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {

    border-color: rgba(0, 255, 170, 0.55) !important;

    box-shadow: 0 0 22px rgba(0, 255, 170, 0.15);

}

code, pre {

    background: rgba(0, 255, 170, 0.08) !important;

    color: #7fffc7 !important;

    border-radius: 4px;

}

a {

    color: #00ffaa !important;

    text-decoration: none;

    border-bottom: 1px dashed rgba(0, 255, 170, 0.5);

}

a:hover {

    color: #00d0ff !important;

    border-bottom-color: #00d0ff;

}

.cyber-banner {

    border: 1px solid rgba(0, 255, 170, 0.35);

    background: linear-gradient(90deg, rgba(0, 255, 170, 0.06), rgba(0, 208, 255, 0.04));

    padding: 14px 18px;

    border-radius: 8px;

    margin-bottom: 18px;

    font-size: 0.9rem;

    letter-spacing: 0.3px;

}

.cyber-banner .tag {

    color: #00ffaa;

    font-weight: 700;

}

.cyber-banner .muted {

    color: #7fa89a;

}

.terminal {

    background: #05110d;

    border: 1px solid rgba(0, 255, 170, 0.35);

    border-left: 3px solid #00ffaa;

    border-radius: 6px;

    padding: 12px 16px;

    font-family: 'JetBrains Mono', monospace;

    font-size: 0.85rem;

    color: #7fffc7;

    margin: 10px 0;

}

.terminal .prompt { color: #00ffaa; }

.terminal .ok { color: #00ffaa; }

.terminal .warn { color: #ffb547; }

@keyframes blink { 50% { opacity: 0; } }

.cursor {

    display: inline-block;

    width: 8px;

    height: 14px;

    background: #00ffaa;

    animation: blink 1s step-start infinite;

    vertical-align: middle;

    margin-left: 4px;

}

</style>

"""

st.markdown(CYBER_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------

# Terms & Conditions gate

# ------------------------------------------------------------------

if "terms_accepted" not in st.session_state:

    st.session_state["terms_accepted"] = False

if not st.session_state.get("terms_accepted", False):

    render_terms_gate()

    st.stop()

# ------------------------------------------------------------------

# Cached search wrapper (backend unchanged)

# ------------------------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)

def cached_search(image_bytes: bytes, _hash: str):

    return run_search(image_bytes)

# ------------------------------------------------------------------

# Pre-compute strings that contain quotes (fixes PEP 701 issues)

# ------------------------------------------------------------------

_FORMATS_DISPLAY = "`, `".join(ALLOWED_EXTENSIONS)

_HELP_TEXT = (

    f"Max {MAX_IMAGE_SIZE_MB} MB · "

    + ", ".join(ALLOWED_EXTENSIONS)

)

_CONSTRAINTS_MD = f"""
- Max size: `{MAX_IMAGE_SIZE_MB} MB`
- Formats: `{_FORMATS_DISPLAY}`
- Cache TTL: `5 min`
- Rate limit: `20/hr`
"""

# ------------------------------------------------------------------

# Sidebar

# ------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
<div style="font-size:2.2rem;">🛰️</div>
<div style="color:#00ffaa; font-weight:700; letter-spacing:2px; font-size:1.05rem;">
    OSINT // VISUAL
</div>
<div style="color:#5fa88e; font-size:0.72rem; letter-spacing:1.5px;">
    REVERSE IMAGE RECON
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Keep the rest of your existing sidebar code below this line.

    st.markdown("### 📡 Session Quota")

    remaining = get_remaining_quota()

    st.progress(

        min(remaining / 20, 1.0),

        text=f"{remaining} / 20 searches remaining",

    )

    st.markdown("---")

    st.markdown("### ⚙️ Protocol")

    st.markdown(
        """
        - **Vision:** Google Cloud Vision
        - **Reverse search:** SerpAPI Google Lens
        - **Transport:** HTTPS
        - **Results:** Matching indexed webpages
        """
    )

st.markdown("---")

st.markdown("### 🔐 Constraints")

st.markdown(_CONSTRAINTS_MD)

st.markdown("---")

st.caption("v1.0 · production build")

# ------------------------------------------------------------------

# Main header

# ------------------------------------------------------------------

st.markdown(
    """
<div class="cyber-banner">
    <span class="tag">[ SYSTEM ONLINE ]</span>
    &nbsp;<span class="muted">|</span>&nbsp;
    Reverse Image Reconnaissance Engine
    &nbsp;<span class="muted">|</span>&nbsp;
    Status: <span class="tag">READY</span>
    <span class="cursor"></span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("# 🛰️ Reverse Image Search")

st.markdown(

"<p style='color:#7fa89a; letter-spacing:0.4px; margin-top:-8px;'>"

"Upload a visual artefact. The engine will analyse its content "

"and locate indexed webpages where it appears."

"</p>",

unsafe_allow_html=True,

)

# ------------------------------------------------------------------

# Upload

# ------------------------------------------------------------------

uploaded_file = st.file_uploader(

"▸ Target Image",

type=ALLOWED_EXTENSIONS,

accept_multiple_files=False,

help=_HELP_TEXT,

)

if uploaded_file is not None:

    col_img, col_info = st.columns([1, 1.6], gap="large")

    with col_img:

        st.markdown("#### ▸ Preview")

        st.image(uploaded_file, caption="", width=340)

    with col_info:

        st.markdown("#### ▸ Target Metadata")

        _meta_md = (

            "```\n"

            f"filename  : {uploaded_file.name}\n"

            f"size      : {uploaded_file.size / 1024:.1f} KB\n"

            f"mime      : {uploaded_file.type}\n"

            "status    : LOADED\n"

            "```"

        )

        st.markdown(_meta_md)

    if st.button(

        "▶ INITIATE SEARCH",

        type="primary",

        use_container_width=True,

    ):

        try:

            image_bytes = validate_image(uploaded_file)

            check_rate_limit()

            with st.spinner(

                "▸ Scanning indexed web for visual matches…"

            ):

                data = cached_search(

                    image_bytes,

                    _hash=str(hash(image_bytes)),

                )

            st.divider()

            render_analysis(data)

            render_results(data)

        except ValidationError as exc:

            st.error(f"⛔ VALIDATION FAILED — {exc}")

        except RuntimeError as exc:

            st.warning(f"⏳ RATE LIMIT — {exc}")

        except Exception as exc:

            logger.exception("Unhandled error during search")

            st.error("⛔ SEARCH ABORTED — internal engine error.")

            with st.expander("▸ Technical trace"):

                st.code(repr(exc))

# ------------------------------------------------------------------

# Privacy policy (dashboard footer)

# ------------------------------------------------------------------

with st.expander("🔒 Privacy Policy & Data Handling", expanded=False):

    render_privacy_policy()