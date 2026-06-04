import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="GCM Level Road Calculator", layout="wide")

# ─── VEHICLE PROFILES ────────────────────────────────────────────────────────────

vehicle_profiles = {
    "Test Vehicle 1": {
        "vehicle_mass": 3500.0,
        "rated_GCM": 8000.0,
        "peak_torque_Nm": 400.0,
        "peak_power_kW": 200.0,
        "final_drive_ratio": 3.70,
        "driveline_efficiency": 0.88,
        "tyre_size": "265/65R17",
        "tyre_radius": 0.380,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "Highway",
        "Cd": 0.40,
        "frontal_area": 3.20,
        "gear_ratios": [4.71, 3.14, 2.11, 1.67, 1.29, 1.00, 0.84, 0.67, 0.60, 0.52],
    },
    "Medium Dual Cab 4WD": {
        "vehicle_mass": 2200.0,
        "rated_GCM": 6000.0,
        "peak_torque_Nm": 500.0,
        "peak_power_kW": 150.0,
        "final_drive_ratio": 3.31,
        "driveline_efficiency": 0.88,
        "tyre_size": "265/65R17",
        "tyre_radius": 0.375,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "All-Terrain",
        "Cd": 0.42,
        "frontal_area": 3.10,
        "gear_ratios": [3.99, 2.37, 1.55, 1.16, 0.85, 0.67],
    },
    "Large Dual Cab 4WD": {
        "vehicle_mass": 2700.0,
        "rated_GCM": 7500.0,
        "peak_torque_Nm": 650.0,
        "peak_power_kW": 170.0,
        "final_drive_ratio": 3.70,
        "driveline_efficiency": 0.87,
        "tyre_size": "285/75R16",
        "tyre_radius": 0.400,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 300.0,
        "tyre_type": "All-Terrain",
        "Cd": 0.45,
        "frontal_area": 3.40,
        "gear_ratios": [4.17, 2.34, 1.52, 1.14, 0.87, 0.69],
    },
    "Full-Size Pickup / 1500 Class": {
        "vehicle_mass": 2500.0,
        "rated_GCM": 7700.0,
        "peak_torque_Nm": 600.0,
        "peak_power_kW": 250.0,
        "final_drive_ratio": 3.92,
        "driveline_efficiency": 0.88,
        "tyre_size": "275/65R18",
        "tyre_radius": 0.400,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "Highway",
        "Cd": 0.50,
        "frontal_area": 3.80,
        "gear_ratios": [4.71, 2.99, 2.14, 1.77, 1.52, 1.27, 1.00, 0.85, 0.69, 0.64],
    },
    "Boxy Wagon 4WD": {
        "vehicle_mass": 2700.0,
        "rated_GCM": 7000.0,
        "peak_torque_Nm": 650.0,
        "peak_power_kW": 200.0,
        "final_drive_ratio": 3.31,
        "driveline_efficiency": 0.88,
        "tyre_size": "285/60R18",
        "tyre_radius": 0.385,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "Highway",
        "Cd": 0.48,
        "frontal_area": 3.30,
        "gear_ratios": [4.17, 2.34, 1.52, 1.14, 0.87, 0.69, 0.58],
    },
    "Custom": {
        "vehicle_mass": 3500.0,
        "rated_GCM": 8000.0,
        "peak_torque_Nm": 400.0,
        "peak_power_kW": 200.0,
        "final_drive_ratio": 3.70,
        "driveline_efficiency": 0.88,
        "tyre_size": "265/65R17",
        "tyre_radius": 0.380,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "Highway",
        "Cd": 0.40,
        "frontal_area": 3.20,
        "gear_ratios": [1.00],
    },
}

# ─── TRAILER PROFILES ────────────────────────────────────────────────────────────

trailer_profiles = {
    "AIC Dual-Axle Flat Front Trailer": {
        "trailer_mass": 3500.0,
        "tow_ball_mass": 200.0,
        "num_axles": 2,
        "num_tyres": 4,
        "tyre_size": "235/75R15",
        "tyre_pressure_kPa": 350.0,
        "tyre_radius": 0.365,
        "tyre_type": "Highway",
        "Cd": 0.55,
        "frontal_width": 2.40,
        "frontal_height": 1.80,
    },
    "Light Load Configuration": {
        "trailer_mass": 1500.0,
        "tow_ball_mass": 100.0,
        "num_axles": 2,
        "num_tyres": 4,
        "tyre_size": "205/75R15",
        "tyre_pressure_kPa": 300.0,
        "tyre_radius": 0.340,
        "tyre_type": "Highway",
        "Cd": 0.55,
        "frontal_width": 2.20,
        "frontal_height": 1.60,
    },
    "Balanced Load Configuration": {
        "trailer_mass": 2500.0,
        "tow_ball_mass": 150.0,
        "num_axles": 2,
        "num_tyres": 4,
        "tyre_size": "225/75R15",
        "tyre_pressure_kPa": 340.0,
        "tyre_radius": 0.355,
        "tyre_type": "Highway",
        "Cd": 0.55,
        "frontal_width": 2.30,
        "frontal_height": 1.70,
    },
    "Heavy Front Load Configuration": {
        "trailer_mass": 3500.0,
        "tow_ball_mass": 350.0,
        "num_axles": 2,
        "num_tyres": 4,
        "tyre_size": "235/75R15",
        "tyre_pressure_kPa": 380.0,
        "tyre_radius": 0.365,
        "tyre_type": "Highway",
        "Cd": 0.55,
        "frontal_width": 2.40,
        "frontal_height": 1.90,
    },
    "Custom": {
        "trailer_mass": 2000.0,
        "tow_ball_mass": 150.0,
        "num_axles": 2,
        "num_tyres": 4,
        "tyre_size": "225/75R15",
        "tyre_pressure_kPa": 340.0,
        "tyre_radius": 0.355,
        "tyre_type": "Highway",
        "Cd": 0.55,
        "frontal_width": 2.30,
        "frontal_height": 1.70,
    },
}

# ─── ROLLING RESISTANCE ESTIMATION ───────────────────────────────────────────────

TYRE_TYPES = ["Highway", "All-Terrain", "Mud-Terrain"]
BASE_CRR = {"Highway": 0.0075, "All-Terrain": 0.011, "Mud-Terrain": 0.015}
REF_PRESSURE_KPA = 280.0  # reference pressure for Crr correction

def estimate_crr(tyre_type, tyre_pressure_kpa):
    """
    Estimate rolling resistance coefficient from tyre type and inflation pressure.
    Higher pressure reduces Crr. Reference pressure is 280 kPa.
    """
    base = BASE_CRR.get(tyre_type, 0.010)
    pressure_factor = (REF_PRESSURE_KPA / max(tyre_pressure_kpa, 50.0)) ** 0.5
    return round(base * pressure_factor, 5)

# ─── CONSTANTS ───────────────────────────────────────────────────────────────────

g = 9.81  # gravitational acceleration, m/s²

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────

st.sidebar.header("Inputs")

# ── Vehicle Profile ──────────────────────────────────────────────────────────────

st.sidebar.subheader("Vehicle Profile")

selected_vehicle = st.sidebar.selectbox(
    "Select Vehicle Profile", list(vehicle_profiles.keys())
)
vp = vehicle_profiles[selected_vehicle]
vk = selected_vehicle  # key prefix for this profile's widgets

m_vehicle = st.sidebar.number_input(
    "Vehicle mass (kg)",
    value=float(vp["vehicle_mass"]),
    min_value=0.0, step=50.0,
    key=f"m_vehicle_{vk}",
)
GCM = st.sidebar.number_input(
    "Rated GCM (kg)",
    value=float(vp["rated_GCM"]),
    min_value=1.0, step=100.0,
    key=f"gcm_{vk}",
)
T_engine = st.sidebar.number_input(
    "Peak engine torque (Nm)",
    value=float(vp["peak_torque_Nm"]),
    min_value=0.0, step=10.0,
    key=f"te_{vk}",
)

# Gear selector — selectbox for named profiles, manual entry for Custom
if selected_vehicle == "Custom":
    gear_ratio = st.sidebar.number_input(
        "Gear ratio",
        value=1.00, min_value=0.01, step=0.01, format="%.3f",
        key=f"gr_{vk}",
    )
else:
    gear_labels = [
        f"Gear {i + 1}  ({r:.3f})" for i, r in enumerate(vp["gear_ratios"])
    ]
    default_gear_idx = len(gear_labels) - 1  # top gear by default
    selected_gear_label = st.sidebar.selectbox(
        "Select Gear for Calculation",
        gear_labels,
        index=default_gear_idx,
        key=f"gear_{vk}",
    )
    gear_ratio = vp["gear_ratios"][gear_labels.index(selected_gear_label)]

final_drive_ratio = st.sidebar.number_input(
    "Final drive ratio",
    value=float(vp["final_drive_ratio"]),
    min_value=0.01, step=0.01, format="%.3f",
    key=f"fdr_{vk}",
)
driveline_efficiency = st.sidebar.number_input(
    "Driveline efficiency (0-1)",
    value=float(vp["driveline_efficiency"]),
    min_value=0.0, max_value=1.0, step=0.01, format="%.2f",
    key=f"de_{vk}",
)
tyre_radius = st.sidebar.number_input(
    "Loaded tyre radius (m)",
    value=float(vp["tyre_radius"]),
    min_value=0.01, step=0.005, format="%.3f",
    key=f"vtr_{vk}",
)
num_vehicle_tyres = int(st.sidebar.number_input(
    "Tyres carrying load",
    value=int(vp["num_vehicle_tyres"]),
    min_value=1, step=1,
    key=f"nvt_{vk}",
))
vehicle_tyre_pressure = st.sidebar.number_input(
    "Tyre pressure (kPa)",
    value=float(vp["tyre_pressure_kPa"]),
    min_value=50.0, step=10.0,
    key=f"vtp_{vk}",
)
vehicle_tyre_type = st.sidebar.selectbox(
    "Tyre type",
    TYRE_TYPES,
    index=TYRE_TYPES.index(vp["tyre_type"]),
    key=f"vtt_{vk}",
)
Cd_vehicle = st.sidebar.number_input(
    "Vehicle Cd",
    value=float(vp["Cd"]),
    min_value=0.0, step=0.01, format="%.2f",
    key=f"cdv_{vk}",
)
A_vehicle = st.sidebar.number_input(
    "Vehicle frontal area (m2)",
    value=float(vp["frontal_area"]),
    min_value=0.1, step=0.1, format="%.2f",
    key=f"afv_{vk}",
)

st.sidebar.divider()

# ── Trailer Profile ───────────────────────────────────────────────────────────────

st.sidebar.subheader("Fixed Dual-Axle Trailer Profile")

selected_trailer = st.sidebar.selectbox(
    "Select Trailer Profile", list(trailer_profiles.keys())
)
tp = trailer_profiles[selected_trailer]
tk = selected_trailer  # key prefix for trailer widgets

m_trailer = st.sidebar.number_input(
    "Trailer mass (kg)",
    value=float(tp["trailer_mass"]),
    min_value=0.0, step=50.0,
    key=f"tm_{tk}",
)
tow_ball_mass = st.sidebar.number_input(
    "Tow ball mass (kg)",
    value=float(tp["tow_ball_mass"]),
    min_value=0.0, step=10.0,
    key=f"tbm_{tk}",
)
num_trailer_tyres = int(st.sidebar.number_input(
    "Number of trailer tyres",
    value=int(tp["num_tyres"]),
    min_value=1, step=1,
    key=f"ntt_{tk}",
))
trailer_tyre_pressure = st.sidebar.number_input(
    "Trailer tyre pressure (kPa)",
    value=float(tp["tyre_pressure_kPa"]),
    min_value=50.0, step=10.0,
    key=f"ttp_{tk}",
)
trailer_tyre_type = st.sidebar.selectbox(
    "Trailer tyre type",
    TYRE_TYPES,
    index=TYRE_TYPES.index(tp["tyre_type"]),
    key=f"ttt_{tk}",
)
trailer_tyre_radius = st.sidebar.number_input(
    "Trailer loaded tyre radius (m)",
    value=float(tp["tyre_radius"]),
    min_value=0.01, step=0.005, format="%.3f",
    key=f"ttr_{tk}",
)
Cd_trailer = st.sidebar.number_input(
    "Trailer Cd",
    value=float(tp["Cd"]),
    min_value=0.0, step=0.01, format="%.2f",
    key=f"cdt_{tk}",
)
frontal_width = st.sidebar.number_input(
    "Trailer frontal width (m)",
    value=float(tp["frontal_width"]),
    min_value=0.1, step=0.05, format="%.2f",
    key=f"fw_{tk}",
)
frontal_height = st.sidebar.number_input(
    "Trailer frontal height (m)",
    value=float(tp["frontal_height"]),
    min_value=0.1, step=0.05, format="%.2f",
    key=f"fh_{tk}",
)

# Trailer frontal area: calculated from width x height, with optional override
A_trailer_calc = frontal_width * frontal_height
override_area = st.sidebar.checkbox(
    "Override trailer frontal area", value=False, key=f"oa_{tk}"
)
if override_area:
    A_trailer = st.sidebar.number_input(
        "Trailer frontal area override (m2)",
        value=round(A_trailer_calc, 2),
        min_value=0.1, step=0.05, format="%.2f",
        key=f"aft_ov_{tk}",
    )
else:
    A_trailer = A_trailer_calc
    st.sidebar.caption(f"Trailer frontal area (w x h): {A_trailer:.2f} m²")

st.sidebar.divider()

# ── Environmental & Operating Conditions ─────────────────────────────────────────

st.sidebar.subheader("Environmental")
air_density = st.sidebar.number_input(
    "Air density (kg/m3)", value=1.225, min_value=0.1, step=0.001, format="%.3f"
)

st.sidebar.divider()

st.sidebar.subheader("Operating Condition")
speed_kmh = st.sidebar.number_input(
    "Vehicle speed (km/h)", value=100.0, min_value=0.0, step=5.0
)

# ─── CALCULATIONS ────────────────────────────────────────────────────────────────

# Speed conversion: km/h to m/s
V = speed_kmh / 3.6

# Mass calculations
m_total = m_vehicle + m_trailer
GCM_utilisation = (m_total / GCM) * 100

# Rolling resistance coefficients estimated from tyre parameters
Crr_vehicle = estimate_crr(vehicle_tyre_type, vehicle_tyre_pressure)
Crr_trailer = estimate_crr(trailer_tyre_type, trailer_tyre_pressure)

# Tyre load calculations
avg_vehicle_load_per_tyre_N = (m_vehicle * g) / num_vehicle_tyres
trailer_tyre_supported_mass = max(0.0, m_trailer - tow_ball_mass)
avg_trailer_load_per_tyre_N = (trailer_tyre_supported_mass * g) / num_trailer_tyres

# Wheel torque = engine torque x gear ratio x final drive ratio x driveline efficiency
T_wheel = T_engine * gear_ratio * final_drive_ratio * driveline_efficiency

# Wheel force = wheel torque / tyre rolling radius
F_wheel = T_wheel / tyre_radius

# Rolling resistance forces (using full masses per Phase 1 formula)
F_rr_vehicle = Crr_vehicle * m_vehicle * g
F_rr_trailer = Crr_trailer * m_trailer * g

# Aerodynamic drag forces
F_aero_vehicle = 0.5 * air_density * Cd_vehicle * A_vehicle * V ** 2
F_aero_trailer = 0.5 * air_density * Cd_trailer * A_trailer * V ** 2

# Total resistance
F_resistance_total = F_rr_vehicle + F_rr_trailer + F_aero_vehicle + F_aero_trailer

# Net tractive force and acceleration
F_net = F_wheel - F_resistance_total
a = F_net / m_total

# Estimated hitch force (force transmitted through towbar to trailer)
F_hitch = m_trailer * a + F_rr_trailer + F_aero_trailer

# ─── MAIN AREA ───────────────────────────────────────────────────────────────────

st.title("GCM Level Road Calculator")
st.markdown(
    """
    **Phase 1 — Level Road Steady-State Calculator.**
    This tool estimates basic towing performance for a vehicle and trailer combination
    on a flat, level road at a single selected vehicle speed. All inputs and outputs use SI units.
    """
)

# Warnings
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

# ─── PROFILE SUMMARY ─────────────────────────────────────────────────────────────

with st.expander("Profile Summary", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Vehicle**")
        st.write(f"Profile: {selected_vehicle}")
        st.write(f"Tyre size: {vp['tyre_size']}")
        st.write(f"Vehicle mass: {m_vehicle:,.0f} kg")
        st.write(f"Rated GCM: {GCM:,.0f} kg")
        st.write(f"Vehicle Cd: {Cd_vehicle:.2f}")
        st.write(f"Vehicle frontal area: {A_vehicle:.2f} m²")
        st.write(f"Tyre type: {vehicle_tyre_type}")
        st.write(f"Tyre pressure: {vehicle_tyre_pressure:.0f} kPa")
        st.write(f"Estimated vehicle Crr: {Crr_vehicle:.5f}")
        st.write(f"Avg vehicle load per tyre: {avg_vehicle_load_per_tyre_N:,.0f} N  ({avg_vehicle_load_per_tyre_N/1000:.2f} kN)")
        st.write(f"Selected gear ratio: {gear_ratio:.3f}")
        st.write(f"Final drive ratio: {final_drive_ratio:.3f}")

    with col2:
        st.markdown("**Trailer**")
        st.write(f"Profile: {selected_trailer}")
        st.write(f"Tyre size: {tp['tyre_size']}")
        st.write(f"Trailer mass: {m_trailer:,.0f} kg")
        st.write(f"Tow ball mass: {tow_ball_mass:,.0f} kg")
        st.write(f"Trailer tyre supported mass: {trailer_tyre_supported_mass:,.0f} kg")
        st.write(f"Trailer Cd: {Cd_trailer:.2f}")
        st.write(f"Trailer frontal area: {A_trailer:.2f} m²  ({frontal_width:.2f} m x {frontal_height:.2f} m)")
        st.write(f"Tyre type: {trailer_tyre_type}")
        st.write(f"Tyre pressure: {trailer_tyre_pressure:.0f} kPa")
        st.write(f"Estimated trailer Crr: {Crr_trailer:.5f}")
        st.write(f"Avg trailer load per tyre: {avg_trailer_load_per_tyre_N:,.0f} N  ({avg_trailer_load_per_tyre_N/1000:.2f} kN)")

    st.markdown("---")
    st.markdown("**Combination**")
    col1, col2, col3 = st.columns(3)
    col1.write(f"Total combination mass: {m_total:,.0f} kg")
    col2.write(f"Rated GCM: {GCM:,.0f} kg")
    col3.write(f"GCM utilisation: {GCM_utilisation:.1f}%")

    st.caption(
        "Rolling resistance is estimated from tyre type, tyre loading, pressure and loaded-radius correction. "
        "Contact patch values are shown as engineering estimates and are not direct rolling resistance measurements."
    )

# ─── MASS CALCULATIONS ───────────────────────────────────────────────────────────

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

# ─── DRIVELINE / TRACTIVE FORCE ──────────────────────────────────────────────────

st.subheader("Driveline / Tractive Force")
col1, col2, col3 = st.columns(3)
col1.metric("Wheel Torque", f"{T_wheel:,.0f} Nm")
col2.metric("Wheel Force", f"{F_wheel:,.0f} N")
col3.metric("Selected Gear Ratio", f"{gear_ratio:.3f}")

# ─── PERFORMANCE ─────────────────────────────────────────────────────────────────

st.subheader("Performance")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Force", f"{F_net:,.0f} N")
col2.metric("Acceleration", f"{a:.4f} m/s2")
col3.metric("Hitch Force (N)", f"{F_hitch:,.0f} N")
col4.metric("Hitch Force (kN)", f"{F_hitch / 1000:.3f} kN")

# ─── FORCE SUMMARY TABLE ─────────────────────────────────────────────────────────

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

# ─── RESISTANCE FORCE BAR CHART ──────────────────────────────────────────────────

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
