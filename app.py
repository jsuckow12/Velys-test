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
    aHKA = mpta - ldfa
    return ldfa, mpta, jlo, aHKA

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

def draw_rotated_line(ax, center, angle_deg, length, color='red', lw=1.5):
    angle_rad = np.radians(angle_deg)
    x0 = center[0] - (length/2) * np.cos(angle_rad)
    y0 = center[1] - (length/2) * np.sin(angle_rad)
    x1 = center[0] + (length/2) * np.cos(angle_rad)
    y1 = center[1] + (length/2) * np.sin(angle_rad)
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw)

def anatomy_diagram(ax, ahka, fma, tma):
    # Set up points: ankle (top), knee (middle), hip (bottom)
    center_x = 0
    ankle_y = 0
    knee_y = 2
    hip_y = 4

    # Calculate offset for aHKA (in degrees)
    angle_rad = np.radians(180 - ahka)
    offset = 1.0 * np.sin(angle_rad)  # horizontal offset for mechanical axis

    # Points
    ankle = (center_x + offset, ankle_y)
    knee = (center_x, knee_y)
    hip = (center_x + offset, hip_y)

    # Draw mechanical axis (ankle to knee to hip)
    ax.plot([ankle[0], knee[0], hip[0]], [ankle[1], knee[1], hip[1]], 'k-', lw=2)
    # Draw points
    ax.plot(*ankle, 'ro', ms=8)
    ax.plot(*knee, 'ro', ms=8)
    ax.plot(*hip, 'ro', ms=8)

    # Draw femoral and tibial joint lines at the knee (same length, red, rotated)
    joint_line_len = 1.2
    # Femoral joint line (above knee): TMA, 0° = horizontal, positive = CCW
    femoral_center = (knee[0], knee[1])
    draw_rotated_line(ax, femoral_center, tma - 90, joint_line_len, color='red', lw=1.5)
    # Tibial joint line (below knee): FMA, 0° = horizontal, positive = CCW (REVERSED)
    tibial_center = (knee[0], knee[1] + 0.2)
    draw_rotated_line(ax, tibial_center, 90 - fma, joint_line_len, color='red', lw=1.5)

    # Labels
    ax.text(*ankle, "Ankle", ha='center', va='bottom', fontsize=10)
    ax.text(*knee, "Knee", ha='center', va='bottom', fontsize=10)
    ax.text(*hip, "Hip", ha='center', va='top', fontsize=10)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-0.5, 4.5)
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
    rHKA = st.number_input("rHKA", value=173, step=1, format="%d")
    FMA = st.number_input("FMA", value=92, step=1, format="%d")
    TMA = st.number_input("TMA", value=84, step=1, format="%d")
    sHKA = st.number_input("sHKA", value=176, step=1, format="%d")

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
    anatomy_diagram(ax1, rHKA, FMA, TMA)
    st.pyplot(fig1)
with ad_col2:
    st.markdown("**Post-op Anatomy**")
    fig2, ax2 = plt.subplots(figsize=(3, 4))
    anatomy_diagram(ax2, post_op_vals["ahka"], post_op_vals["fma"], post_op_vals["tma"])
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
