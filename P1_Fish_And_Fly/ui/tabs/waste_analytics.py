import streamlit as st
import matplotlib.pyplot as plt
import time

# -----------------------------
# STATE
# -----------------------------
if "waste_insights_log" not in st.session_state:
    st.session_state.waste_insights_log = []


# -----------------------------
# 🧠 INSIGHT ENGINE
# -----------------------------
def generate_waste_insights(df):

    insights = []

    try:
        # -------------------------
        # FILTERS
        # -------------------------
        targets = df[df["entity_role"] == "COLLECTION_TARGET"]
        collected = targets[targets["final_action_status"] == "COLLECTED"]

        hazards = df[df["entity_role"] == "NAVIGATION_HAZARD"]

        # -------------------------
        # CURRENT STATUS
        # -------------------------
        insights.append(
            f"Collected {len(collected)} out of {len(targets)} targets"
        )

        # -------------------------
        # DOMINANT WASTE TYPE
        # -------------------------
        if not collected.empty:
            type_counts = collected["class_name"].value_counts()

            top_type = type_counts.idxmax()
            pct = type_counts.max() / len(collected)

            if pct > 0.5:
                insights.append(f"{top_type} is dominant in collected waste")
            else:
                insights.append("Waste distribution is diverse")

        # -------------------------
        # COLLECTION PERFORMANCE
        # -------------------------
        if len(targets) > 0:
            rate = len(collected) / len(targets)

            if rate > 0.7:
                insights.append("High collection efficiency")
            elif rate < 0.4:
                insights.append("Low collection efficiency — improvement needed")

        # -------------------------
        # NAVIGATION HAZARD AWARENESS
        # -------------------------
        if not hazards.empty:
            hazard_types = hazards["class_name"].unique()

            for h in hazard_types:
                insights.append(f"Navigation hazard detected: {h}")

    except:
        insights.append("Waste insight error")

    return insights


# -----------------------------
# MAIN UI
# -----------------------------
def render_waste(df):

    st.subheader("♻️ Waste Intelligence")

    if df is None or df.empty:
        st.warning("No object data available")
        return

    # -----------------------------
    # INFO SECTIONS
    # -----------------------------
    with st.expander("ℹ️ What this tab shows"):
        st.markdown("""
This tab evaluates real cleaning impact and environmental awareness.

It focuses on collected garbage targets, while also detecting navigation hazards
that influence mission safety.
""")

    with st.expander("🔍 What to see"):
        st.markdown("""
• Distribution of collected garbage → pollution pattern  
• Collection efficiency → system effectiveness  
• Hazard detection → navigation risks  
""")

    # -----------------------------
    # KPI (ENTITY ROLE BASED)
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    targets = df[df["entity_role"] == "COLLECTION_TARGET"]
    env = df[df["entity_role"] == "ENVIRONMENT_ENTITY"]
    hazards = df[df["entity_role"] == "NAVIGATION_HAZARD"]

    col1.metric("Collection Targets", len(targets))
    col2.metric("Environment Entities", len(env))
    col3.metric("Navigation Hazards", len(hazards))
    col4.metric("Total Objects", len(df))

    # -----------------------------
    # FILTERED DATA
    # -----------------------------
    collected = targets[targets["final_action_status"] == "COLLECTED"]

    # -----------------------------
    # LAYOUT
    # -----------------------------
    left, center, right = st.columns([1.2, 2.5, 1.5])

    # -----------------------------
    # LEFT PANEL (TARGET SUMMARY)
    # -----------------------------
    with left:
        st.markdown("### 🎯 Target Summary")

        status_counts = targets["final_action_status"].value_counts()

        for k, v in status_counts.items():
            st.write(f"• {k}: {v}")

    # -----------------------------
    # CENTER (GRAPH)
    # -----------------------------
    with center:

        if not collected.empty:

            type_counts = collected["class_name"].value_counts()

            fig, ax = plt.subplots(figsize=(5, 2.5))

            ax.bar(range(len(type_counts)), type_counts.values)

            ax.set_xticks(range(len(type_counts)))
            ax.set_xticklabels(type_counts.index, rotation=45)

            ax.set_title("Collected Garbage Type Distribution")
            ax.set_ylabel("Count")

            ax.grid(alpha=0.3)

            st.pyplot(fig, width="stretch")

        else:
            st.info("No garbage collected yet")

    # -----------------------------
    # RIGHT PANEL (INSIGHTS)
    # -----------------------------
    with right:
        st.markdown("### 🧠 Waste Insights")

        insights = generate_waste_insights(df)
        now = time.time()

        for ins in insights:
            if not any(ins == old[0] for old in st.session_state.waste_insights_log):
                st.session_state.waste_insights_log.append((ins, now))

        # Keep last 2 min
        st.session_state.waste_insights_log = [
            (m, t) for m, t in st.session_state.waste_insights_log
            if now - t <= 120
        ]

        for msg, t in st.session_state.waste_insights_log[::-1]:
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