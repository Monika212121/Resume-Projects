import streamlit as st
import matplotlib.pyplot as plt

CLASSES = ["plastic_bag","plastic_bottle","glass_bottle","metal_can","fishing_net","fishing_rope","algae_bloom"]

def render_waste(df):

    st.markdown("""
### What to see

Bars represent garbage classes detected by the system.

Even if a class is not detected yet, it still appears in the chart.
""")

    counts = {c:0 for c in CLASSES}

    vc = df["class_name"].value_counts()

    for k,v in vc.items():
        if k in counts:
            counts[k]=v

    fig,ax = plt.subplots()

    ax.bar(counts.keys(),counts.values(),color="teal")

    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(counts.keys(), rotation=45)

    st.pyplot(fig)