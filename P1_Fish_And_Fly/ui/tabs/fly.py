import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


FLY_LOG_PATH = "artifacts/logs/fly_state_deltas.csv"


def render_fly(stats=None):
    # ===============================
    #  FLY MACHINE OVERVIEW
    # ===============================
    st.subheader("Fly Machine")

    st.markdown(
        """
        **Responsibility:**  
        The Fly machine continuously **monitors the Fish machine’s health, communication stability,
        and operational progress**, ensuring mission safety, responsiveness, and early failure detection.
        """
    )

    st.markdown(
        "[View Fly Documentation](#)",
        unsafe_allow_html=True
    )

    st.divider()

    # ===============================
    # LOAD FLY TELEMETRY
    # ===============================
    try:
        df = pd.read_csv(FLY_LOG_PATH)
    except FileNotFoundError:
        st.info("Fly telemetry data not available yet.")
        return

    if df.empty:
        st.info("Waiting for Fly telemetry data...")
        return

    # ===============================
    # 🩺 SYSTEM HEALTH SNAPSHOT
    # ===============================
    st.subheader("System Health Snapshot")

    latest = df.iloc[-1]

    c1, c2, c3 = st.columns(3)
    #c1.metric("Fish Alive", "YES" if latest["alive"] else "NO")
    c1.metric("Machine damage(in %)", 0)
    c2.metric("Fish Status", latest["status"])
    c3.metric("Silence Δ (sec)", round(latest["silence_delta"], 3))

    st.divider()

    # ===============================
    # 📊 BEHAVIORAL DELTAS ANALYSIS
    # ===============================
    st.subheader("Behavioral Deltas Analysis")

    delta_means = {
        "Communication Δ": df["communication_delta"].mean(),
        "Progress Δ": df["fish_progress_delta"].mean(),
        "Silence Δ": df["silence_delta"].mean(),
    }

    # --- ORANGE BAR CHART ---
    fig, ax = plt.subplots(figsize =(6,3))

    ax.bar(
        delta_means.keys(),
        delta_means.values(),
        color="orange"
    )

    ax.set_ylabel("Average Delta Value", fontsize=9)
    ax.set_title("Average Fly Monitoring Deltas", fontsize=11)

    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.set_xticklabels(delta_means.keys(), rotation=20)

    fig.tight_layout()

    st.pyplot(fig)

    # ===============================
    # 📈 OPTIONAL: RAW TREND (BONUS)
    # ===============================
    st.subheader("Delta Trends Over Time")

    st.line_chart(
        df[[
            "communication_delta",
            "fish_progress_delta",
            "silence_delta"
        ]]
    )
