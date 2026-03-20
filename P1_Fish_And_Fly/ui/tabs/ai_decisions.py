import streamlit as st
import matplotlib.pyplot as plt

def render_ai(df):

    st.markdown("""
### What to see

This page explains how the AI decides whether an object
should be collected, ignored, or avoided.
""")

    status = df["decision_status"].value_counts()

    fig,ax = plt.subplots()

    ax.bar(status.index,status.values,color="purple")

    st.pyplot(fig)