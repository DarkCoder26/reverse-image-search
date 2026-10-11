"""Consent gate for the Reverse Image Search Streamlit application."""

import streamlit as st


def render_terms_gate() -> bool:
    """Show the privacy/usage gate and record consent using app.py's session key."""
    consent_key = "terms_accepted"

    if st.session_state.get(consent_key, False):
        return True

    st.markdown("## Privacy and usage notice")
    st.warning(
        "When you run a reverse image search, the selected image may be sent to "
        "configured third-party services, such as Google Cloud Vision and/or "
        "SerpAPI Google Lens, for analysis. These providers process requests under "
        "their own applicable terms and privacy policies. Results are possible "
        "matches, not proof of who uploaded an image."
    )

    with st.expander("Before you continue", expanded=True):
        st.markdown(
            "- Upload only images you have permission to process.\n"
            "- Avoid uploading confidential or sensitive images.\n"
            "- Results depend on provider coverage and the image supplied."
        )

    accepted = st.checkbox(
        "I understand and agree to continue.",
        key="terms_gate_checkbox",
    )

    if st.button(
        "Accept and continue",
        type="primary",
        disabled=not accepted,
        key="terms_gate_accept_button",
    ):
        st.session_state[consent_key] = True
        st.rerun()

    st.info("Accept the notice above to use the search application.")
    st.stop()
    return False
