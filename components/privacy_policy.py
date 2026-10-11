"""Privacy policy component for the Streamlit reverse image search app."""

import textwrap
import streamlit as st


def render_privacy_policy() -> None:
    html = textwrap.dedent("""\
<div style="
    background: rgba(0, 208, 255, 0.04);
    border: 1px solid rgba(0, 208, 255, 0.15);
    border-radius: 8px;
    padding: 16px 20px;
    color: #a7d8ec;
    font-size: 0.85rem;
    line-height: 1.6;
">
    <h4 style="color:#00d0ff; margin-top:0;">Data Handling Disclosure</h4>
    <p>
        This tool performs <b>reverse image search</b> by transmitting
        uploaded images to third-party visual-recognition services.
    </p>
    <ul>
        <li><b>Image transmission:</b> Images may be sent to Google Cloud Vision
        and/or SerpAPI (Google Lens) for analysis.</li>
        <li><b>Third-party providers:</b> Processing is subject to the providers'
        applicable terms and privacy policies.</li>
        <li><b>Image storage:</b> Retention depends on the application's
        implementation and provider policies.</li>
        <li><b>Your responsibility:</b> Avoid uploading sensitive images without
        understanding how they may be processed.</li>
    </ul>
    <p style="color:#7fa89a; font-size:0.78rem;">
        Last updated: October 2026
    </p>
</div>
""")
    st.markdown(html, unsafe_allow_html=True)
