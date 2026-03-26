import streamlit as st
import time
import matplotlib.pyplot as plt

# -----------------------------
# STATE
# -----------------------------
if "ai_insights_log" not in st.session_state:
    st.session_state.ai_insights_log = []

if "decision_memory" not in st.session_state:
    st.session_state.decision_memory = set()


# -----------------------------
# 🧠 INSIGHT ENGINE (JARVIS MODE)
# -----------------------------
def generate_ai_insights(df):

    insights = []

    try:
        recent = df.tail(40)

        # -------------------------
        # DECISION REASON ANALYSIS
        # -------------------------
        reason_counts = recent["decision_reason"].value_counts()

        for reason, count in reason_counts.items():
            key = f"reason_{reason}"

            if key not in st.session_state.decision_memory:
                insights.append(f"AI frequently making decisions due to: {reason}")
                st.session_state.decision_memory.add(key)

        # -------------------------
        # CONFIDENCE ANALYSIS
        # -------------------------
        avg_conf = recent["avg_confidence"].mean()

        if avg_conf < 0.5:
            insights.append("Low confidence detections → model uncertainty high")
        elif avg_conf > 0.8:
            insights.append("High confidence detections → strong model reliability")

        # -------------------------
        # PRIORITY VS ACTION
        # -------------------------
        high_priority_ignored = recent[
            (recent["priority_score"] > 0.7) &
            (recent["final_action_status"] == "IGNORED")
        ]

        if len(high_priority_ignored) > 0:
            insights.append("High priority targets ignored → critical decision flaw")

        # -------------------------
        # DECISION CONSISTENCY
        # -------------------------
        mismatch = (
            recent["decision_status"] != recent["final_action_status"]
        ).sum()

        if mismatch > 0:
            insights.append("Decision-action mismatch → execution inconsistency")

        # -------------------------
        # BEHAVIOR PATTERN
        # -------------------------
        collect_rate = (recent["final_action_status"] == "COLLECTED").mean()

        if collect_rate > 0.7:
            insights.append("Aggressive collection strategy active")
        elif collect_rate < 0.3:
            insights.append("Conservative filtering strategy active")

        # -------------------------
        # CURRENT DECISION STATUS
        # -------------------------
        latest = df.iloc[-1]

        insights.insert(
            0,
            f"Current Decision: {latest['decision_status']} → {latest['final_action_status']} ({latest['decision_reason']})"
        )

    except Exception as e:
        insights.append("AI insight error")

    return insights


# -----------------------------
# MAIN UI
# -----------------------------
def render_decisions_ai(df):

    st.subheader("🧠 AI Decision Intelligence")

    if df is None or df.empty:
        st.warning("No object data available")
        return

    # -----------------------------
    # INFO SECTIONS
    # -----------------------------
    with st.expander("ℹ️ What this tab shows"):
        st.markdown("""
This tab explains AI decision-making in real-time.

It reveals WHY objects are collected, ignored, or avoided,
based on confidence, priority, and environmental reasoning.
""")

    with st.expander("🔍 What to see"):
        st.markdown("""
• Low confidence → model uncertainty  
• High priority ignored → critical flaw  
• Avoid decisions → navigation risk  
• Decision mismatch → execution issue  
""")

    latest = df.iloc[-1]

    # -----------------------------
    # KPI
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Avg Confidence", f"{df['avg_confidence'].mean():.2f}")
    col2.metric("Avg Priority", f"{df['priority_score'].mean():.2f}")

    collect_rate = (df["final_action_status"] == "COLLECTED").mean()
    col3.metric("Collection Rate", f"{collect_rate:.2f}")

    mismatch = (df["decision_status"] != df["final_action_status"]).mean()
    col4.metric("Mismatch Rate", f"{mismatch:.2f}")

    # -----------------------------
    # LAYOUT
    # -----------------------------
    left, center, right = st.columns([1.2, 2.5, 1.5])

    # -----------------------------
    # LEFT PANEL (LIVE DECISION)
    # -----------------------------
    with left:
        st.markdown("### 🤖 Live Decision")

        st.write(f"Object: {latest['class_name']}")
        st.write(f"Decision: {latest['decision_status']}")
        st.write(f"Action: {latest['final_action_status']}")
        st.write(f"Reason: {latest['decision_reason']}")
        st.write(f"Confidence: {latest['avg_confidence']:.2f}")
        st.write(f"Priority: {latest['priority_score']:.2f}")

    # -----------------------------
    # CENTER (GRAPH)
    # -----------------------------
    with center:

        # -------- DECISION DISTRIBUTION --------
        decision_counts = df["final_action_status"].value_counts()

        fig1, ax1 = plt.subplots(figsize=(5, 2))
        ax1.bar(decision_counts.index, decision_counts.values)
        ax1.set_title("Final Action Distribution")
        ax1.grid(alpha=0.3)

        st.pyplot(fig1, width="stretch")

    # -----------------------------
    # RIGHT PANEL (INSIGHTS)
    # -----------------------------
    with right:
        st.markdown("### 🧠 AI Insights")

        insights = generate_ai_insights(df)
        now = time.time()

        for ins in insights:
            if not any(ins == old[0] for old in st.session_state.ai_insights_log):
                st.session_state.ai_insights_log.append((ins, now))

        st.session_state.ai_insights_log = [
            (m, t) for m, t in st.session_state.ai_insights_log if now - t <= 120
        ]

        for msg, t in st.session_state.ai_insights_log[::-1]:
            age = now - t

            if age < 10:
                st.markdown(f"**• {msg}**")
            elif age < 60:
                st.markdown(f"• {msg}")
            else:
                st.markdown(
                    f"<span style='color:gray'>• {msg}</span>",
                    unsafe_allow_html=True
                )