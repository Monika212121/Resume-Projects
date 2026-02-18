import streamlit as st
import matplotlib.pyplot as plt



def render_fish(stats):
    # ===============================
    #  FISH MACHINE OVERVIEW
    # ===============================
    st.subheader(" Fish Machine")

    st.markdown(
        """
        **Responsibility:**  
        The Fish machine is responsible for **detecting, tracking, and physically collecting garbage**
        from the water surface and underwater environment, ensuring successful removal and
        categorization of waste objects during the mission.
        """
    )

    # 🔗 Project documentation link (you can change later)
    st.markdown(
        "[View Fish Documentaion](#)",
        unsafe_allow_html=True
    )

    st.divider()

    # ===============================
    # 🗑️ GARBAGE COLLECTION ANALYSIS
    # ===============================
    st.subheader("Garbage Collection Analysis")

    final_stats = stats.final_state_stats()

    if not final_stats:
        st.info("No garbage collection data available yet.")
        return

    col_left, col_right = st.columns(2)

    # --- Bar Chart (Final State) ---
    with col_left:
        st.markdown("**Final State Distribution (Bar Chart)**")
        st.bar_chart(final_stats)

    # --- Pie Chart (Final State) ---
    with col_right:
        st.markdown("**Final State Distribution (Pie Chart)**")

        fig, ax = plt.subplots()
        ax.pie(
            final_stats.values(),
            labels=final_stats.keys(),
            autopct="%1.1f%%",
            startangle=90
        )
        ax.axis("equal")
        st.pyplot(fig)

    st.divider()

    # ==========================================
    # ♻️ COLLECTED GARBAGE – CLASS ANALYSIS
    # ==========================================
    st.subheader("Collected Garbage Class Analysis")

    df = stats.df

    if df.empty or "final_state" not in df.columns or "class_name" not in df.columns:
        st.info("Class-wise garbage data not available.")
        return

    collected_df = df[df["final_state"] == "COLLECTED"]

    if collected_df.empty:
        st.info("No garbage has been collected yet.")
        return

    class_counts = (
        collected_df["class_name"]
        .value_counts()
        .to_dict()
    )

    col_left, col_right = st.columns(2)

    # --- Bar Chart (Class-wise Collected) ---
    with col_left:
        st.markdown("**Collected Garbage by Class (Bar Chart)**")
        st.bar_chart(class_counts)

    # --- Pie Chart (Class-wise Collected) ---
    with col_right:
        st.markdown("**Collected Garbage by Class (Pie Chart)**")

        fig, ax = plt.subplots()
        ax.pie(
            class_counts.values(),
            labels=class_counts.keys(),
            autopct="%1.1f%%",
            startangle=90
        )
        ax.axis("equal")
        st.pyplot(fig)


    c1, c2, c3 = st.columns(3)
    c1.metric("Total Collected", final_stats.get("COLLECTED", 0))
    c2.metric("Total Lost", final_stats.get("LOST", 0))
    c3.metric("Total Ignored", final_stats.get("IGNORED", 0))