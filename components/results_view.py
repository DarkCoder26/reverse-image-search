"""
Cyber-themed rendering for search results.
"""
import streamlit as st
from models.result import AnalysisResult, MatchType


MATCH_ICONS = {
    MatchType.EXACT.value: "🎯",
    MatchType.PARTIAL.value: "✂️",
    MatchType.PAGE.value: "📄",
    MatchType.VISUAL.value: "👁️",
    MatchType.SOURCE.value: "🏠",
}

MATCH_COLORS = {
    MatchType.EXACT.value: "#00ffaa",
    MatchType.PARTIAL.value: "#ffb547",
    MatchType.PAGE.value: "#00d0ff",
    MatchType.VISUAL.value: "#b88cff",
    MatchType.SOURCE.value: "#ff7ac6",
}


def _terminal_line(label: str, value: str, ok: bool = True) -> str:
    mark = "OK" if ok else "!!"
    color = "#00ffaa" if ok else "#ffb547"
    return (
        f"<span style='color:#5fa88e;'>{label:>12}</span>  "
        f"<span style='color:{color};'>[{mark}]</span>  "
        f"<span style='color:#c8f7e4;'>{value}</span>"
    )


def render_analysis(data: AnalysisResult) -> None:
    """Render the 'what the image looks like' section."""
    if not (data.labels or data.entities):
        return

    st.markdown("## 🧠 Visual Signature")

    lines = []
    if data.labels:
        lines.append(
            _terminal_line("LABELS", ", ".join(data.labels))
        )
    if data.entities:
        lines.append(
            _terminal_line(
                "ENTITIES",
                ", ".join(data.entities[:8]),
            )
        )
    if data.providers_used:
        lines.append(
            _terminal_line(
                "ENGINES",
                ", ".join(data.providers_used),
            )
        )

    st.markdown(
        "<div class='terminal'>" + "<br>".join(lines) + "</div>",
        unsafe_allow_html=True,
    )


def render_results(data: AnalysisResult) -> None:
    """Render the list of reverse-image-search hits."""
    if data.errors:
        for err in data.errors:
            st.warning(f"⚠️ {err}")

    if not data.results:
        st.markdown(
            "<div class='terminal'>"
            "<span class='prompt'>$</span> search --reverse<br>"
            "<span class='warn'>[!!]</span>  "
            "No matching webpages were found."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"<div class='terminal'>"
        f"<span class='prompt'>$</span> search --reverse<br>"
        f"<span class='ok'>[OK]</span>  "
        f"{data.total_results} match(es) located "
        f"across {len(data.providers_used)} engine(s)"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("## 🌐 Reconnaissance Report")

    # Group by match type
    groups: dict[str, list] = {}
    for r in data.results:
        groups.setdefault(r.match_type.value, []).append(r)

    order = [
        MatchType.EXACT.value,
        MatchType.SOURCE.value,
        MatchType.PARTIAL.value,
        MatchType.VISUAL.value,
        MatchType.PAGE.value,
    ]

    for match_type in order:
        items = groups.get(match_type)
        if not items:
            continue

        icon = MATCH_ICONS.get(match_type, "🔗")
        color = MATCH_COLORS.get(match_type, "#00ffaa")

        st.markdown(
            f"<h3 style='color:{color}; text-shadow:0 0 8px "
            f"{color}55; margin-top:18px;'>"
            f"{icon} {match_type} "
            f"<span style='color:#5fa88e; font-size:0.7em;'>"
            f"· {len(items)} hit(s)</span></h3>",
            unsafe_allow_html=True,
        )

        for i, r in enumerate(items, start=1):
            with st.container(border=True):
                cols = st.columns([1, 5, 1.2])

                # Thumbnail
                with cols[0]:
                    if r.thumbnail:
                        try:
                            st.image(r.thumbnail, width=90)
                        except Exception:
                            st.markdown(
                                "<div style='width:90px; height:90px; "
                                "background:rgba(0,255,170,0.05); "
                                "border:1px solid rgba(0,255,170,0.2); "
                                "border-radius:6px;'></div>",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.markdown(
                            "<div style='width:90px; height:90px; "
                            "background:rgba(0,255,170,0.05); "
                            "border:1px solid rgba(0,255,170,0.2); "
                            "border-radius:6px; display:flex; "
                            "align-items:center; justify-content:center; "
                            "color:#5fa88e; font-size:0.7rem;'>"
                            "NO IMG</div>",
                            unsafe_allow_html=True,
                        )

                # Details
                with cols[1]:
                    st.markdown(
                        f"<div style='font-size:1.02rem; "
                        f"color:#00ffaa; font-weight:700; "
                        f"letter-spacing:0.4px;'>"
                        f"{r.platform}"
                        f"<span style='color:#5fa88e; "
                        f"font-weight:400; font-size:0.82rem; "
                        f"margin-left:8px;'>"
                        f"· via {r.provider.value}</span></div>",
                        unsafe_allow_html=True,
                    )

                    if r.title:
                        st.markdown(
                            f"<div style='color:#a7d8ec; "
                            f"font-size:0.85rem; "
                            f"margin-top:2px;'>{r.title}</div>",
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        f"<a href='{r.url}' target='_blank' "
                        f"style='font-size:0.85rem; "
                        f"word-break:break-all;'>{r.url}</a>",
                        unsafe_allow_html=True,
                    )

                # Score
                with cols[2]:
                    st.markdown(
                        f"<div style='text-align:right;'>"
                        f"<div style='color:#5fa88e; "
                        f"font-size:0.7rem; letter-spacing:1px;'>"
                        f"CONFIDENCE</div>"
                        f"<div style='color:{color}; "
                        f"font-size:1.4rem; font-weight:700; "
                        f"text-shadow:0 0 10px {color}66;'>"
                        f"{r.score:.2f}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )