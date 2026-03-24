"""
Reusable floating-card components for Streamlit pages.

Usage
─────
    from components.cards import inject_floating_card_css, floating_card, metric_card

    # Call once per page, before any card is rendered.
    inject_floating_card_css()

    # Render a simple floating card
    floating_card("Hello world")

    # Render a metric card (centred value with title)
    metric_card("Total Students", "1,000")
"""

import streamlit as st

# ──────────────────────────────────────────────
# CSS injection (call once per page)
# ──────────────────────────────────────────────

_FLOATING_CARD_CSS = """
<style>
/* ── Floating card ── */
.floating-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.floating-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.2);
}

/* ── Metric card (centred KPI) ── */
.metric-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}
.metric-title {
    color: #64748b;
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.metric-value {
    color: #0f172a;
    font-size: 2.5rem;
    font-weight: 800;
}

/* ── Shared helper classes ── */
.exp-title   { color: #0f172a !important; font-weight: 700; font-size: 1.2rem; margin-bottom: 0.2rem; }
.exp-company { color: #4f46e5 !important; font-weight: 600; font-size: 1.1rem; }
.exp-meta    { color: #64748b !important; font-size: 0.9rem; margin-bottom: 0.8rem; }
.resume-bullet { margin-bottom: 0.5rem; line-height: 1.5; color: #334155; }
.social-link { text-decoration: none; color: #4f46e5 !important; font-weight: 600; margin-right: 15px; }
.skill-tag   { background: #e0e7ff; color: #4f46e5 !important; padding: 2px 10px;
               border-radius: 12px; font-size: 0.8rem; font-weight: 600;
               display: inline-block; margin: 2px 4px 2px 0; border: 1px solid #c7d2fe; }

/* ── Streamlit bordered containers floating effect (for chart cards) ── */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > .element-container .chart-container-marker) {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin-bottom: 2rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > .element-container .chart-container-marker):hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1) !important;
}
</style>
"""


def inject_floating_card_css() -> None:
    """Inject the shared floating-card CSS into the page.

    Call this **once** at the top of every Streamlit page that uses cards.
    """
    st.markdown(_FLOATING_CARD_CSS, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Card helpers
# ──────────────────────────────────────────────

def floating_card(content_html: str) -> None:
    """Render a floating card that wraps arbitrary HTML content.

    Parameters
    ----------
    content_html : str
        Raw HTML string to place inside the card's ``<div>``.
    """
    st.markdown(
        f"<div class='floating-card'>{content_html}</div>",
        unsafe_allow_html=True,
    )


def metric_card(title: str, value: str) -> None:
    """Render a centred metric / KPI card.

    Parameters
    ----------
    title : str
        Small uppercase label shown above the value.
    value : str
        The big number or text to display prominently.
    """
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-title">{title}</div>'
        f'<div class="metric-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def chart_container():
    """Create a floating chart container.
    
    Returns a Streamlit container object that has the floating card styling applied.
    """
    c = st.container(border=True)
    c.markdown('<div class="chart-container-marker" style="display: none;"></div>', unsafe_allow_html=True)
    return c
