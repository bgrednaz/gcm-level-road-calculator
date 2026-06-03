import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="GCM Level Road Calculator", layout="wide")

st.title("GCM Level Road Calculator")
st.markdown(
    """
    **Phase 1 — Level Road Steady-State Calculator.**
    This tool estimates basic towing performance for a vehicle and trailer combination
    on a flat, level road at a single selected vehicle speed. All inputs and outputs use SI units.
    """
)

# ─── SIDEBAR INPUTS ────────────────────────────────────────────────────────────

st.sidebar.header("Inputs")

# 1. Vehicle Mass Inputs
st.sidebar.subheader("1. Vehicle Mass")
m_vehicle = st.sidebar.number_input(
    "Vehicle mass (kg)", value=3500.0, min_value=0.0, step=50.0
)
m_trailer = st.sidebar.number_input(
    "Trailer mass (kg)", value=3500.0, min_value=0.0, step=50.0
)
GCM = st.sidebar.number_input(
    "Rated Gross Combination Mass - GCM (kg)", value=8000.0, min_value=1.0, step=100.0
)

# 2. Driveline Inputs
st.sidebar.subheader("2. Driveline")
T_engine = st.sidebar.number_input(
    "Engine torque (Nm)", value=400.0, min_value=0.0, step=10.0
)
gear_ratio = st.sidebar.number_input(
    "Gear ratio", value=3.5, min_value=0.01, step=0.1, format="%.2f"
)
final_drive_ratio = st.sidebar.number_input(
    "Final drive ratio", value=3.7, min_value=0.01, step=0.1, format="%.2f"
)
driveline_efficiency = st.sidebar.number_input(
    "Driveline efficiency (0-1)", value=0.88, min_value=0.0, max_value=1.0,
    step=0.01, format="%.2f"
)
tyre_radius = st.sidebar.number_input(
    "Tyre rolling radius (m)", value=0.38, min_value=0.01, step=0.01, format="%.3f"
)

# 3. Aerodynamic Inputs
st.sidebar.subheader("3. Aerodynamics")
air_density = st.sidebar.number_input(
    "Air density (kg/m3)", value=1.225, min_value=0.1, step=0.001, format="%.3f"
)
Cd_vehicle = st.sidebar.number_input(
    "Vehicle drag coefficient (Cd)", value=0.35, min_value=0.0, step=0.01, format="%.2f"
)
A_vehicle = st.sidebar.number_input(
    "Vehicle frontal area (m2)", value=3.5, min_value=0.1, step=0.1, format="%.2f"
)
Cd_trailer = st.sidebar.number_input(
    "Trailer drag coefficient (Cd)", value=0.55, min_value=0.0, step=0.01, format="%.2f"
)
A_trailer = st.sidebar.number_input(
    "Trailer frontal area (m2)", value=4.5, min_value=0.1, step=0.1, format="%.2f"
)

# 4. Rolling Resistance Inputs
st.sidebar.subheader("4. Rolling Resistance")
Crr_vehicle = st.sidebar.number_input(
    "Vehicle rolling resistance coefficient", value=0.008, min_value=0.0,
    step=0.001, format="%.4f"
)
Crr_trailer = st.sidebar.number_input(
    "Trailer rolling resistance coefficient", value=0.010, min_value=0.0,
    step=0.001, format="%.4f"
)

# 5. Operating Condition
st.sidebar.subheader("5. Operating Condition")
speed_kmh = st.sidebar.number_input(
    "Vehicle speed (km/h)", value=100.0, min_value=0.0, step=5.0
)

# ─── CONSTANTS ─────────────────────────────────────────────────────────────────

g = 9.81  # gravitational acceleration, m/s²

# ─── CALCULATIONS ──────────────────────────────────────────────────────────────

# Convert speed from km/h to m/s
V = speed_kmh / 3.6

# Total combination mass
m_total = m_vehicle + m_trailer

# GCM utilisation as a percentage
GCM_utilisation = (m_total / GCM) * 100

# Wheel torque = engine torque x gear ratio x final drive ratio x driveline efficiency
T_wheel = T_engine * gear_ratio * final_drive_ratio * driveline_efficiency

# Wheel force = wheel torque / tyre rolling radius
F_wheel = T_wheel / tyre_radius

# Rolling resistance force: vehicle and trailer
F_rr_vehicle = Crr_vehicle * m_vehicle * g
F_rr_trailer = Crr_trailer * m_trailer * g

# Aerodynamic drag force: vehicle and trailer
F_aero_vehicle = 0.5 * air_density * Cd_vehicle * A_vehicle * V ** 2
F_aero_trailer = 0.5 * air_density * Cd_trailer * A_trailer * V ** 2

# Total resistance force
F_resistance_total = F_rr_vehicle + F_rr_trailer + F_aero_vehicle + F_aero_trailer

# Net tractive force available for acceleration
F_net = F_wheel - F_resistance_total

# Acceleration: F = ma  ->  a = F_net / m_total
a = F_net / m_total

# Estimated hitch force (force transmitted through towbar to trailer)
F_hitch = m_trailer * a + F_rr_trailer + F_aero_trailer

# ─── WARNINGS ──────────────────────────────────────────────────────────────────

gcm_exceeded = m_total > GCM
net_negative = F_net < 0

if gcm_exceeded:
    st.error(
        f"WARNING: Total combination mass {m_total:,.0f} kg exceeds "
        f"rated GCM of {GCM:,.0f} kg by {m_total - GCM:,.0f} kg."
    )

if net_negative:
    st.warning(
        f"WARNING: Net force is {F_net:,.0f} N. "
        "The vehicle cannot maintain speed or accelerate at the selected condition."
    )

# ─── RESULTS ───────────────────────────────────────────────────────────────────

# Mass Calculations
st.subheader("Mass Calculations")
col1, col2, col3 = st.columns(3)
col1.metric("Total Combination Mass", f"{m_total:,.0f} kg")
col2.metric(
    "GCM Utilisation",
    f"{GCM_utilisation:.1f}%",
    delta=f"{GCM_utilisation - 100:.1f}% over limit" if gcm_exceeded else None,
    delta_color="inverse",
)
col3.metric("Rated GCM", f"{GCM:,.0f} kg")

# Driveline / Tractive Force
st.subheader("Driveline / Tractive Force")
col1, col2 = st.columns(2)
col1.metric("Wheel Torque", f"{T_wheel:,.0f} Nm")
col2.metric("Wheel Force", f"{F_wheel:,.0f} N")

# Performance
st.subheader("Performance")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Force", f"{F_net:,.0f} N")
col2.metric("Acceleration", f"{a:.4f} m/s2")
col3.metric("Hitch Force (N)", f"{F_hitch:,.0f} N")
col4.metric("Hitch Force (kN)", f"{F_hitch / 1000:.3f} kN")

# ─── FORCE SUMMARY TABLE ───────────────────────────────────────────────────────

st.subheader("Force Summary Table")

summary_data = {
    "Force Component": [
        "Vehicle Rolling Resistance",
        "Trailer Rolling Resistance",
        "Vehicle Aerodynamic Drag",
        "Trailer Aerodynamic Drag",
        "Total Resistance",
        "Wheel Force (Tractive)",
        "Net Force",
        "Hitch Force",
    ],
    "Value (N)": [
        round(F_rr_vehicle, 1),
        round(F_rr_trailer, 1),
        round(F_aero_vehicle, 1),
        round(F_aero_trailer, 1),
        round(F_resistance_total, 1),
        round(F_wheel, 1),
        round(F_net, 1),
        round(F_hitch, 1),
    ],
    "Value (kN)": [
        round(F_rr_vehicle / 1000, 3),
        round(F_rr_trailer / 1000, 3),
        round(F_aero_vehicle / 1000, 3),
        round(F_aero_trailer / 1000, 3),
        round(F_resistance_total / 1000, 3),
        round(F_wheel / 1000, 3),
        round(F_net / 1000, 3),
        round(F_hitch / 1000, 3),
    ],
}
df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

# ─── RESISTANCE FORCE BAR CHART ────────────────────────────────────────────────

st.subheader("Resistance Force Breakdown")

categories = [
    "Vehicle\nRolling Resistance",
    "Trailer\nRolling Resistance",
    "Vehicle\nAero Drag",
    "Trailer\nAero Drag",
]
values = [F_rr_vehicle, F_rr_trailer, F_aero_vehicle, F_aero_trailer]
colors = ["#1976D2", "#64B5F6", "#E64A19", "#FF8A65"]

fig, ax = plt.subplots(figsize=(9, 4))
bars = ax.bar(categories, values, color=colors, edgecolor="white", linewidth=0.8)

for bar, val in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max(values) * 0.01,
        f"{val:,.0f} N",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
    )

ax.set_ylabel("Force (N)", fontsize=11)
ax.set_title("Resistance Forces at Selected Speed", fontsize=12, fontweight="bold")
ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 100)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
