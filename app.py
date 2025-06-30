import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Lower Limb Analyzer", layout="wide")
st.title("Lower Limb Analyzer (Web Version)")

# --- Helper functions ---

def calculate_cpak(fma, tma):
    ldfa = 180 - fma
    mpta = tma
    jlo = mpta + ldfa
    ahka = mpta - ldfa
    return ldfa, mpta, jlo, ahka

def calculate_post_op(pre_op, technique):
    if technique == "Mechanical Alignment (MA)":
        return {
            "ahka": 180,
            "fma": 90,
            "tma": 90,
            "shka": 180
        }
    elif technique == "Kinematic Alignment (KA)":
        jlca = pre_op["ahka"] - pre_op["shka"]
        ahka_prime = pre_op["ahka"] - jlca
        return {
            "ahka": ahka_prime,
            "fma": pre_op["fma"],
            "tma": pre_op["tma"],
            "shka": pre_op["shka"]
        }
    else:  # Inverse Kinematic Alignment (iKA)
        tma = pre_op["tma"]
        if tma < 87:
            tma_prime = 87
        elif tma <= 90 and tma >= 87:
            tma_prime = tma
        else:
            tma_prime = 90
        fma_prime = tma_prime
        return {
            "ahka": 180,
            "fma": fma_prime,
            "tma": tma_prime,
            "shka": 180
        }

def anatomy_diagram(ax, ahka):
    # Draw a simple version of the lines and red dots
    center_x = 0
    hip_y = 0
    knee_y = 2
    tibia_length = 0.5
    ankle_y = knee_y + tibia_length + 1.6

    # Calculate offset for aHKA
    angle_rad = np.radians(180 - ahka)
    total_x_offset = (tibia_length + 1.6) * np.sin(angle_rad)
    hip_x = center_x + total_x_offset
    knee_x = center_x
    tibia_x = knee_x + tibia_length * np.sin(angle_rad)
    tibia_y = knee_y + tibia_length * np.cos(angle_rad)
    ankle_x = hip_x

    # Draw lines
    ax.plot([hip_x, knee_x], [hip_y, knee_y], 'k-', lw=2)
    ax.plot([tibia_x, ankle_x], [tibia_y, ankle_y], 'k-', lw=2)
    # Draw points
    ax.plot([hip_x, knee_x, tibia_x, ankle_x], [hip_y, knee_y, tibia_y, ankle_y], 'ro', ms=8)
    # Draw labels
    ax.text(hip_x, hip_y-0.1, "Hip", ha='center', fontsize=10)
    ax.text(ankle_x, ankle_y+0.1, "Ankle", ha='center', fontsize=10)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-0.5, 4)
    ax.axis('off')
    ax.set_title("Anatomy Diagram")

def cpak_graph(ax, ahka, jlo, color, label):
    # Reverse y-axis to match PyQt5
    ax.axhline(180, color='gray', linestyle='--', linewidth=1)
    ax.axvline(0, color='gray', linestyle='--', linewidth=1)
    ax.scatter([ahka], [jlo], color=color, s=100, label=label)
    ax.set_xlabel("aHKA")
    ax.set_ylabel("JLO")
    ax.set_xlim(-8, 8)
    ax.set_ylim(190, 170)  # Reverse y-axis
    ax.set_title("CPAK Plot")
    ax.legend()

# --- Streamlit UI ---

col1, col2 = st.columns(2)

with col1:
    st.header("Pre-op Input")
    rHKA = st.number_input("rHKA", value=173.0)
    FMA = st.number_input("FMA", value=92.0)
    TMA = st.number_input("TMA", value=84.0)
    sHKA = st.number_input("sHKA", value=176.0)

with col2:
    st.header("Post-op Input")
    technique = st.selectbox("Surgical Technique", ["Mechanical Alignment (MA)", "Kinematic Alignment (KA)", "Inverse Kinematic Alignment (iKA)"])

# --- Calculations ---

pre_op = {"ahka": rHKA, "fma": FMA, "tma": TMA, "shka": sHKA}
ldfa_pre, mpta_pre, jlo_pre, ahka_pre = calculate_cpak(FMA, TMA)
post_op_vals = calculate_post_op(pre_op, technique)
ldfa_post, mpta_post, jlo_post, ahka_post = calculate_cpak(post_op_vals["fma"], post_op_vals["tma"])

# --- Display Anatomy Diagrams ---

st.subheader("Anatomy Diagrams")
ad_col1, ad_col2 = st.columns(2)
with ad_col1:
    st.markdown("**Pre-op Anatomy**")
    fig1, ax1 = plt.subplots(figsize=(3, 4))
    anatomy_diagram(ax1, rHKA)
    st.pyplot(fig1)
with ad_col2:
    st.markdown("**Post-op Anatomy**")
    fig2, ax2 = plt.subplots(figsize=(3, 4))
    anatomy_diagram(ax2, post_op_vals["ahka"])
    st.pyplot(fig2)

# --- Display CPAK Graphs and Tables ---

st.subheader("CPAK Graphs and Tables")
cg_col1, cg_col2 = st.columns(2)

with cg_col1:
    st.markdown("**Pre-op CPAK**")
    fig3, ax3 = plt.subplots(figsize=(4, 4))
    cpak_graph(ax3, ahka_pre, jlo_pre, 'red', 'Pre-op')
    st.pyplot(fig3)
    st.table({
        "LDFA": [f"{ldfa_pre:.2f}"],
        "MPTA": [f"{mpta_pre:.2f}"],
        "JLO": [f"{jlo_pre:.2f}"],
        "aHKA": [f"{ahka_pre:.2f}"]
    })

with cg_col2:
    st.markdown("**Post-op CPAK**")
    fig4, ax4 = plt.subplots(figsize=(4, 4))
    cpak_graph(ax4, ahka_post, jlo_post, 'blue', 'Post-op')
    st.pyplot(fig4)
    st.table({
        "LDFA": [f"{ldfa_post:.2f}"],
        "MPTA": [f"{mpta_post:.2f}"],
        "JLO": [f"{jlo_post:.2f}"],
        "aHKA": [f"{ahka_post:.2f}"]
    })
