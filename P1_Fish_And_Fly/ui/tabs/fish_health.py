import streamlit as st
import matplotlib.pyplot as plt

def render_health(states):

    st.markdown("""
### What to see

• Communication delta spikes indicate connection delays  
• Silence delta measures time since last robot signal
""")

    fig,ax = plt.subplots()

    ax.plot(states["communication_delta"],color="red")
    ax.set_title("Communication Delay")

    st.pyplot(fig)

    fig,ax = plt.subplots()

    ax.plot(states["fish_progress_delta"],color="green")
    ax.set_title("Fish Progress Delta")

    st.pyplot(fig)

    fig,ax = plt.subplots()

    ax.plot(states["silence_delta"],color="orange")
    ax.set_title("Robot Silence Time")

    st.pyplot(fig)