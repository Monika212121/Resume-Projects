import time
import streamlit as st
import matplotlib.pyplot as plt

import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from src.common.logging import logger

# -------------------------
# STATE (Maintaining Insight, Milestones and Phase transition History)
# -------------------------
if "insight_log" not in st.session_state:
    st.session_state.insight_log = []

if "milestones_triggered" not in st.session_state:
    st.session_state.milestones_triggered = set()

if "phase_transitions" not in st.session_state:
    st.session_state.phase_transitions = set()

# -------------------------------------------------
# METRICS
# -------------------------------------------------
def compute_exploration_rate(df, window=10):
    try:
        if len(df) < window:
            return 0.0

        recent = df.tail(window)
        delta = recent["surface_coverage_pct"].iloc[-1] - recent["surface_coverage_pct"].iloc[0]

        return max(0.0, delta / window)
    except:
        return 0.0


def compute_efficiency_score(df, window=20):
    try:
        if len(df) < window:
            return 0.0

        recent = df.tail(window)

        coverage_gain = recent["surface_coverage_pct"].iloc[-1] - recent["surface_coverage_pct"].iloc[0]
        movement = recent["fish_progress_delta"].abs().sum()

        return 0.0 if movement == 0 else max(0.0, coverage_gain / movement)
    except:
        return 0.0


# -------------------------------------------------
# ALERT ENGINE
# -------------------------------------------------
def generate_alerts(df):
    alerts = []

    try:
        phase = df.iloc[-1]["mission_phase"]

        if phase == "ABORT":
            alerts.append(("critical", "🚨 Mission ABORTED"))
        elif phase == "RETURN_HQ":
            alerts.append(("critical", "Fish Machine returning Base HQ"))
        elif phase == "UNLOADING":
            alerts.append(("warning", "📦 Unloading in progress"))
        elif phase == "DONE":
            alerts.append(("success", "✅ Mission completed"))

        if compute_exploration_rate(df) < 0.01:
            alerts.append(("warning", "⚠️ Exploration stagnating"))

    except:
        alerts.append(("warning", "⚠️ Alert system error"))

    return alerts


# -------------------------------------------------
# MILESTONE DETECTION (FIXED)
# -------------------------------------------------
def detect_milestones(series, label):
    insights = []
    milestones = [25, 50, 75, 100]

    try:
        current_val = series.iloc[-1]

        for m in milestones:
            key = f"{label}_{m}"

            # If crossed AND not already triggered
            if current_val >= m and key not in st.session_state.milestones_triggered:
                insights.append(f"{label} crossed {m}% coverage")
                st.session_state.milestones_triggered.add(key)

        logger.info(f"detect_milestones(), insights: {insights}")


    except Exception as e:
        logger.error(f"Milestone error: {e}")

    return insights


# -------------------------------------------------
# CURRENT STATUS
# -------------------------------------------------
def get_current_status(df):
    try:
        phase = df.iloc[-1]["mission_phase"]
        exploration_rate = compute_exploration_rate(df)
        eff = compute_efficiency_score(df)

        if phase == "SURFACE":
            if exploration_rate >= 0.05:
                return "🌊 Surface cleaning — high efficiency sweep"
            elif exploration_rate >= 0.01 and exploration_rate < 0.05:
                return "🌊 Surface cleaning — steady progress"
            else:
                return "🌊 Surface cleaning — possible stagnation"

        elif phase == "UNDERWATER":
            if exploration_rate >= 0.05:
                return "🤿 Underwater cleaning — high efficiency sweep"
            elif exploration_rate >= 0.01 and exploration_rate < 0.05:
                return "🤿 Underwater cleaning — steady progress"
            else:
                return "🤿 Underwater cleaning — possible stagnation"

        elif phase == "UNLOADING":
            return "📦 Unloading collected waste — temporary pause in coverage"

        elif phase == "RETURN_HQ":
            return "🔄 Returning to base HQ — mission wrap-up phase"

        elif phase == "DONE":
            return "✅ Mission completed"

        return "ℹ️ Monitoring mission state"

    except:
        return "⚠️ Unable to determine current status"


# -------------------------------------------------
# INSIGHTS
# -------------------------------------------------

def detect_phase_transitions(df):
    insights = []

    try:
        phases = df["mission_phase"].tail(10).tolist()              # recent window

        for i in range(1, len(phases)):
            prev = phases[i - 1]
            curr = phases[i]

            if prev != curr:
                key = f"{prev}->{curr}"

                if key not in st.session_state.phase_transitions:
                    insights.append(f"Mission Phase Transition: {prev} → {curr}")
                    st.session_state.phase_transitions.add(key)

    except Exception as e:
        logger.error(f"Phase Transition error: {e}")

    return insights


def generate_insights(df):
    insights = []

    try:
        surface = df["surface_coverage_pct"]
        underwater = df["underwater_coverage_pct"]

        # Phase Transition
        if len(df) > 1:
            insights += detect_phase_transitions(df)

        # Milestones
        if surface.max() > 0 and underwater.max() == 0:
            insights += detect_milestones(surface, "Surface")

        if underwater.max() > 0:
            insights += detect_milestones(underwater, "Underwater")

        # Stagnation
        if compute_exploration_rate(df) < 0.01:
            insights.append("📉 Navigation slowed")

        # Status always first
        insights.insert(0, get_current_status(df))

    except:
        insights.append("Insight error")

    return insights


# -------------------------------------------------
# PDF EXPORT (FULL LOG)
# -------------------------------------------------
def generate_pdf_report(df, alerts):

    latest = df.iloc[-1]
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Mission Intelligence Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    header = f"""
    Latest Mission Phase: {latest['mission_phase']}<br/>
    Latest Fish machine State: {latest["fish_state"]}<br/>
    Latest Surface Level Coverage: {latest['surface_coverage_pct']:.2f}%<br/>
    Latest Underwater Level Coverage: {latest['underwater_coverage_pct']:.2f}%<br/>
    """

    elements.append(Paragraph(header, styles["Normal"]))
    elements.append(Spacer(1, 10))

    # Insights (FULL LOG)
    elements.append(Paragraph("Insights (Last 10 min)", styles["Heading2"]))

    for msg, _ in st.session_state.insight_log:
        clean = msg.encode("ascii", "ignore").decode()
        elements.append(Paragraph(f"- {clean}", styles["Normal"]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Alerts", styles["Heading2"]))

    for _, a in alerts:
        clean = a.encode("ascii", "ignore").decode()
        elements.append(Paragraph(f"- {clean}", styles["Normal"]))

    doc.build(elements)

    return open(tmp_pdf.name, "rb").read()


# -------------------------------------------------
# 🎬 MAIN UI
# -------------------------------------------------
def render_mission_intelligence(telemetry_df):

    top_left, top_right = st.columns([6, 1])

    with top_left:
        st.subheader("Mission Intelligence")

    if telemetry_df is None or telemetry_df.empty:
        st.warning("No telemetry data available")
        return

    telemetry_df = telemetry_df.sort_values("timestamp")
    latest = telemetry_df.iloc[-1]

    # -------------------------
    # INFO
    # -------------------------
    with st.expander("ℹ️ What this page shows"):
        st.markdown("""
This page provides mission-level intelligence by analyzing coverage progression,
Fish machine efficiency, and operational behavior in real-time.
                    
It also evaluates both speed and quality of cleaning operation.
""")

    with st.expander("🔍 What to look for"):
        st.markdown("""
• Increasing coverage → effective navigation 
• Flat curves → unloading garbage bin or inefficiency  
• Exploration Rate → speed of progress, Efficiency Score → quality of movement
""")
        
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Surface Level Coverage", f"{latest['surface_coverage_pct']:.2f}%")
    col2.metric("Underwater Level Coverage", f"{latest['underwater_coverage_pct']:.2f}%")
    col3.metric("Exploration Rate", f"{compute_exploration_rate(telemetry_df):.3f}")
    col4.metric("Efficiency Score", f"{compute_efficiency_score(telemetry_df):.3f}")

    left, center, right = st.columns([1, 3.0, 1.5])

    # Timeline
    with left:
        st.markdown("### Mission Timeline")
        for p in telemetry_df["mission_phase"].tail(10)[::-1]:
            st.write(f"• {p}")

    # Graph
    with center:
        fig, ax = plt.subplots(figsize=(5.0, 2.5))
        ax.plot(telemetry_df["surface_coverage_pct"], label="Surface")
        ax.plot(telemetry_df["underwater_coverage_pct"], label="Underwater")
        ax.set_title("Coverage Dynamics (Surface Vs Underwater)")
        ax.set_xlabel("Mission Time (Ticks)")
        ax.set_ylabel("Coverage Area (%)")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig, width="stretch")

    # Alerts + Insights
    with right:
        st.markdown("### 🚨 Alerts")
        alerts = generate_alerts(telemetry_df)

        for level, msg in alerts:
            getattr(st, {"critical": "error", "warning": "warning", "success": "success"}[level])(msg)

        st.markdown("### 🧠 Operational Insights")

        insights = generate_insights(telemetry_df)
        now = time.time()

        # Deduplicated insert
        for ins in insights:
            if not any(ins == old[0] for old in st.session_state.insight_log):
                st.session_state.insight_log.append((ins, now))

        # Keep last 2 min
        st.session_state.insight_log = [
            (m, t) for m, t in st.session_state.insight_log if now - t <= 120
        ]

        # Render (faded)
        for msg, t in st.session_state.insight_log[::-1]:
            age = now - t

            if age < 15:                                        # fresh info -> bold text
                st.markdown(f"**• {msg}**")
            elif age < 60:                                      # before 1 min -> normal text
                st.markdown(f"• {msg}")
            else:                                               # stale -> fainted grey text
                st.markdown(f"<span style='color:gray'>• {msg}</span>", unsafe_allow_html=True)

    # PDF Export
    pdf = generate_pdf_report(telemetry_df, alerts)

    with top_right:
        st.download_button("📄 Export PDF", pdf, "mission_report.pdf")

    return