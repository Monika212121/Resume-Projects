import streamlit as st
import time
import matplotlib.pyplot as plt

# -----------------------------
# STATE
# -----------------------------
if "health_insights_log" not in st.session_state:
    st.session_state.health_insights_log = []

if "health_summary_log" not in st.session_state:
    st.session_state.health_summary_log = []

if "last_summary_time" not in st.session_state:
    st.session_state.last_summary_time = time.time()


# -----------------------------
# 🧠 CORE INSIGHT ENGINE
# -----------------------------
def generate_health_insights(df):

    insights = []

    try:
        latest = df.iloc[-1]

        silence = df["silence_delta"].tail(20).mean()
        comm = df["communication_delta"].tail(20).mean()
        movement = df["fish_progress_delta"].tail(20).mean()

        # -------------------------
        # CURRENT SYSTEM STATE
        # -------------------------
        if latest["fish_state"] != "ALIVE":
            insights.append("🚨 System not operational")

        # -------------------------
        # COMMUNICATION HEALTH
        # -------------------------
        if comm > 0.1:
            insights.append("⚠️ High communication latency detected")
        elif comm < 0.01:
            insights.append("✅ Communication stable")

        # -------------------------
        # SILENCE ANALYSIS
        # -------------------------
        if silence > 0.5:
            insights.append("⚠️ Increasing silence → possible signal drop")
        elif silence < 0.1:
            insights.append("✅ Active communication maintained")

        # -------------------------
        # MOVEMENT HEALTH
        # -------------------------
        if movement < 0.05:
            insights.append("⚠️ Low mobility → possible blockage or idle state")
        elif movement > 0.3:
            insights.append("🚀 High mobility → aggressive exploration")

        # -------------------------
        # TREND DETECTION
        # -------------------------
        if df["communication_delta"].tail(10).is_monotonic_increasing:
            insights.append("📈 Communication degrading over time")

        if df["fish_progress_delta"].tail(10).is_monotonic_decreasing:
            insights.append("📉 Mobility decreasing → efficiency drop")

        # -------------------------
        # ALWAYS ADD CURRENT STATUS
        # -------------------------
        insights.insert(
            0,
            f"Current Health: State={latest['fish_state']}, Comm={comm:.3f}, Move={movement:.3f}"
        )

    except:
        insights.append("Health insight error")

    return insights


# -----------------------------
# ⏱️ 3-MIN PERFORMANCE SUMMARY
# -----------------------------
def generate_performance_summary(df):

    try:
        window = df.tail(180)  # ~3 min (assuming 1 sec refresh)

        comm = window["communication_delta"].mean()
        silence = window["silence_delta"].mean()
        movement = window["fish_progress_delta"].mean()

        summary = []

        # Communication summary
        if comm < 0.02:
            summary.append("Communication remained stable")
        else:
            summary.append("Communication showed latency spikes")

        # Silence summary
        if silence < 0.1:
            summary.append("Continuous signal maintained")
        else:
            summary.append("Intermittent silence observed")

        # Movement summary
        if movement > 0.2:
            summary.append("Efficient movement maintained")
        else:
            summary.append("Movement efficiency reduced")

        return " | ".join(summary)

    except:
        return "Performance summary unavailable"


# -----------------------------
# MAIN UI
# -----------------------------
def render_health(df):

    st.subheader("🐟 Fish System Health Intelligence")

    if df is None or df.empty:
        st.warning("No telemetry data available")
        return

    # -----------------------------
    # INFO SECTIONS
    # -----------------------------
    with st.expander("ℹ️ What this tab shows"):
        st.markdown("""
This tab monitors system-level health of the fish robot.

It analyzes communication stability, movement efficiency, and signal behavior
to detect early signs of system degradation.
""")

    with st.expander("🔍 What to see"):
        st.markdown("""
• High communication latency → system lag  
• Increasing silence → signal loss risk  
• Low mobility → blockage or inefficiency  
• Trends → early failure detection  
""")

    latest = df.iloc[-1]

    # -----------------------------
    # KPI
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Fish State", latest["fish_state"])
    col2.metric("Comm Latency", f"{latest['communication_delta']:.3f}")
    col3.metric("Silence", f"{latest['silence_delta']:.3f}")
    col4.metric("Movement", f"{latest['fish_progress_delta']:.3f}")

    # -----------------------------
    # LAYOUT
    # -----------------------------
    left, center, right = st.columns([1.2, 2.5, 1.5])

    # -----------------------------
    # LEFT PANEL
    # -----------------------------
    with left:
        st.markdown("### 🧬 System Signals")

        st.write("Recent Status:")
        for state in df["fish_state"].tail(8).tolist()[::-1]:
            st.write(f"• {state}")

    # -----------------------------
    # CENTER GRAPH
    # -----------------------------
    with center:

        fig, ax = plt.subplots(figsize=(5, 2.5))

        ax.plot(df["communication_delta"], label="Communication")
        ax.plot(df["silence_delta"], label="Silence")
        ax.plot(df["fish_progress_delta"], label="Movement")

        ax.set_title("System Health Signals")
        ax.legend()
        ax.grid(alpha=0.3)

        st.pyplot(fig, width="stretch")

    # -----------------------------
    # RIGHT PANEL (INSIGHTS)
    # -----------------------------
    with right:
        st.markdown("### 🧠 Health Insights")

        insights = generate_health_insights(df)
        now = time.time()

        for ins in insights:
            if not any(ins == old[0] for old in st.session_state.health_insights_log):
                st.session_state.health_insights_log.append((ins, now))

        # Keep last 2 minutes
        st.session_state.health_insights_log = [
            (m, t) for m, t in st.session_state.health_insights_log if now - t <= 120
        ]

        for msg, t in st.session_state.health_insights_log[::-1]:
            age = now - t

            if age < 10:
                st.markdown(f"**• {msg}**")
            elif age < 60:
                st.markdown(f"• {msg}")
            else:
                st.markdown(f"<span style='color:gray'>• {msg}</span>", unsafe_allow_html=True)

        # -----------------------------
        # ⏱️ PERFORMANCE SUMMARY (3 MIN)
        # -----------------------------
        if time.time() - st.session_state.last_summary_time > 180:

            summary = generate_performance_summary(df)

            st.session_state.health_summary_log.append(
                (f"🧾 3-min Summary: {summary}", now)
            )

            st.session_state.last_summary_time = time.time()

        # Show summaries
        st.markdown("### 🧾 Performance Summary")

        for msg, t in st.session_state.health_summary_log[::-1]:
            st.markdown(f"<span style='color:gray'>• {msg}</span>", unsafe_allow_html=True)