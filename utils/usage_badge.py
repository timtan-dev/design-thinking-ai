"""
Display utility for cost and duration badges
Shows usage metrics for AI-generated content
"""

import streamlit as st
from config.model_pricing import format_cost, format_duration


def display_usage_badge(duration_seconds=None, cost_usd=None, input_tokens=None, output_tokens=None):
    """
    Display a compact usage badge showing cost and duration

    Args:
        duration_seconds: Time taken for generation (float)
        cost_usd: Cost in USD (float)
        input_tokens: Number of input tokens (int)
        output_tokens: Number of output tokens (int)
    """
    if not duration_seconds and not cost_usd:
        return  # Nothing to display

    # Build badge HTML
    badge_parts = []

    if duration_seconds:
        duration_str = format_duration(duration_seconds)
        badge_parts.append(f'<span class="usage-badge-item">⏱️ {duration_str}</span>')

    if cost_usd:
        cost_str = format_cost(cost_usd)
        badge_parts.append(f'<span class="usage-badge-item">💰 {cost_str}</span>')

    if input_tokens or output_tokens:
        total_tokens = (input_tokens or 0) + (output_tokens or 0)
        tokens_str = f"{total_tokens:,}" if total_tokens < 1000 else f"{total_tokens/1000:.1f}k"
        badge_parts.append(f'<span class="usage-badge-item">🔢 {tokens_str}</span>')

    if badge_parts:
        badge_html = f"""
        <div class="usage-badge">
            {' · '.join(badge_parts)}
        </div>
        """
        st.markdown(badge_html, unsafe_allow_html=True)


def display_usage_details(duration_seconds=None, cost_usd=None, input_tokens=None, output_tokens=None, model_used=None):
    """
    Display detailed usage information in an expander

    Args:
        duration_seconds: Time taken for generation (float)
        cost_usd: Cost in USD (float)
        input_tokens: Number of input tokens (int)
        output_tokens: Number of output tokens (int)
        model_used: AI model used (string)
    """
    with st.expander("📊 Usage Details", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            if duration_seconds:
                st.metric("Duration", format_duration(duration_seconds))
            else:
                st.metric("Duration", "N/A")

        with col2:
            if cost_usd:
                st.metric("Cost", format_cost(cost_usd))
            else:
                st.metric("Cost", "N/A")

        with col3:
            if input_tokens or output_tokens:
                total_tokens = (input_tokens or 0) + (output_tokens or 0)
                st.metric("Total Tokens", f"{total_tokens:,}")
            else:
                st.metric("Total Tokens", "N/A")

        if input_tokens or output_tokens or model_used:
            st.divider()

            if model_used:
                st.caption(f"**Model:** {model_used}")

            if input_tokens:
                st.caption(f"**Input Tokens:** {input_tokens:,}")

            if output_tokens:
                st.caption(f"**Output Tokens:** {output_tokens:,}")


def inject_usage_badge_css():
    """
    Inject CSS styles for usage badges
    Call this once at the top of your page
    """
    st.markdown("""
    <style>
    .usage-badge {
        display: inline-block;
        padding: 4px 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        font-size: 0.85em;
        color: white;
        margin: 4px 0;
        font-weight: 500;
    }

    .usage-badge-item {
        margin: 0 4px;
    }

    .usage-badge-compact {
        display: inline-block;
        padding: 2px 8px;
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 8px;
        font-size: 0.75em;
        color: #667eea;
        margin: 2px 4px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)


def display_compact_usage(duration_seconds=None, cost_usd=None):
    """
    Display a very compact inline usage badge (for table cells, list items, etc.)

    Args:
        duration_seconds: Time taken for generation (float)
        cost_usd: Cost in USD (float)
    """
    if not duration_seconds and not cost_usd:
        return ""

    parts = []
    if duration_seconds:
        parts.append(format_duration(duration_seconds))
    if cost_usd:
        parts.append(format_cost(cost_usd))

    badge_html = f'<span class="usage-badge-compact">{" · ".join(parts)}</span>'
    return badge_html
