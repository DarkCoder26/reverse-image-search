"""
Simple in-session rate limiter backed by st.session_state.
For multi-instance production, replace with Redis.
"""
import time
import streamlit as st
from config.settings import load_config


def _init_state():
    if "_rl_timestamps" not in st.session_state:
        st.session_state["_rl_timestamps"] = []


def check_rate_limit() -> None:
    """
    Raise ``RuntimeError`` if the session has exceeded its quota.

    Quota is configured via ``RATE_LIMIT`` and ``RATE_WINDOW``
    in secrets / env.
    """
    _init_state()
    cfg = load_config()

    now = time.time()
    window_start = now - cfg.rate_limit_window

    # Drop expired entries
    st.session_state["_rl_timestamps"] = [
        ts for ts in st.session_state["_rl_timestamps"]
        if ts >= window_start
    ]

    if len(st.session_state["_rl_timestamps"]) >= cfg.rate_limit_per_session:
        remaining = int(
            st.session_state["_rl_timestamps"][0]
            + cfg.rate_limit_window - now
        )
        raise RuntimeError(
            f"Rate limit reached. Try again in {remaining}s."
        )

    st.session_state["_rl_timestamps"].append(now)


def get_remaining_quota() -> int:
    """Return how many searches remain in the current window."""
    _init_state()
    cfg = load_config()
    now = time.time()
    window_start = now - cfg.rate_limit_window

    active = [
        ts for ts in st.session_state["_rl_timestamps"]
        if ts >= window_start
    ]
    return max(0, cfg.rate_limit_per_session - len(active))