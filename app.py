import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Lower Limb Analyzer", layout="wide")

st.title("Lower Limb Analyzer (Web Version)")

# Sidebar for user input
st.sidebar.header("Input Values")
rHKA = st.sidebar.number_input("rHKA", value=173.0)
FMA = st.sidebar.number_input("FMA", value=92.0)
TMA = st.sidebar.number_input("TMA", value=84.0)
sHKA = st.sidebar.number_input("sHKA", value=176.0)

# CPAK calculations
def calculate_cpak(fma, tma):
    ldfa = 180 - fma
    mpta = tma
    jlo = mpta + ldfa
    ahka = mpta - ldfa
    return ldfa, mpta, jlo, ahka

ldfa, mpta, jlo, ahka = calculate_cpak(FMA, TMA)

# Show table
st.subheader("CPAK Values")
st.table({
    "LDFA": [f"{ldfa:.2f}"],
    "MPTA": [f"{mpta:.2f}"],
    "JLO": [f"{jlo:.2f}"],
    "aHKA": [f"{ahka:.2f}"]
})

# Show CPAK graph
st.subheader("CPAK Graph")
fig, ax = plt.subplots(figsize=(5, 5))
ax.axhline(180, color='gray', linestyle='--', linewidth=1)
ax.axvline(0, color='gray', linestyle='--', linewidth=1)
ax.scatter([ahka], [jlo], color='red', s=100)
ax.set_xlabel("aHKA")
ax.set_ylabel("JLO")
ax.set_xlim(-8, 8)
ax.set_ylim(170, 190)
ax.set_title("CPAK Plot")
st.pyplot(fig)
