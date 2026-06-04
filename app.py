import re
import math
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

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────────

TYRE_TYPES = ["Highway", "All-Terrain", "Mud-Terrain"]

# Phase 1 Crr base values (pressure-corrected, for steady-state section)
BASE_CRR_P1 = {"Highway": 0.0075, "All-Terrain": 0.011, "Mud-Terrain": 0.015}
REF_PRESSURE_KPA = 280.0

def estimate_crr(tyre_type, tyre_pressure_kpa):
    """
    Phase 1: Estimate Crr from tyre type and pressure only.
    Higher pressure reduces Crr. Reference is 280 kPa.
    """
    base = BASE_CRR_P1.get(tyre_type, 0.010)
    pressure_factor = (REF_PRESSURE_KPA / max(tyre_pressure_kpa, 50.0)) ** 0.5
    return round(base * pressure_factor, 5)


# Phase 2A Crr base values (tyre-type only, before loaded-radius correction)
BASE_CRR_P2 = {"Highway": 0.010, "All-Terrain": 0.013, "Mud-Terrain": 0.017}

def calc_crr_p2(tyre_type, loaded_radius_m, unloaded_radius_m):
    """
    Phase 2A: Estimate Crr using tyre type as the base, then apply a
    loaded-radius deflection correction.
      loaded_radius_ratio = loaded_radius / unloaded_radius
      Crr_adjusted = Crr_base × (1 + 2.5 × max(0, 1 − loaded_radius_ratio))
    A tyre carrying more load deflects more (lower loaded_radius_ratio),
    which increases its rolling resistance.
    """
    base = BASE_CRR_P2.get(tyre_type, 0.012)
    if unloaded_radius_m <= 0:
        return base
    loaded_radius_ratio = loaded_radius_m / unloaded_radius_m
    crr = base * (1.0 + 2.5 * max(0.0, 1.0 - loaded_radius_ratio))
    return crr


def parse_tyre_size(tyre_str):
    """
    Parse a tyre size string such as "265/65R17".
    Returns a dict with geometric properties, or None if the string cannot
    be parsed.

    Calculation:
      section_width_m  = width_mm / 1000
      sidewall_height_m = section_width_m × (aspect_ratio / 100)
      rim_diameter_m   = rim_diameter_inches × 0.0254
      unloaded_diameter_m = rim_diameter_m + 2 × sidewall_height_m
      unloaded_radius_m   = unloaded_diameter_m / 2
    """
    match = re.match(r"(\d+)/(\d+)[Rr](\d+(?:\.\d+)?)", tyre_str.strip())
    if not match:
        return None
    width_mm = float(match.group(1))
    aspect_pct = float(match.group(2))
    rim_in = float(match.group(3))

    section_width_m = width_mm / 1000.0
    sidewall_m = section_width_m * (aspect_pct / 100.0)
    rim_diameter_m = rim_in * 0.0254
    unloaded_diameter_m = rim_diameter_m + 2.0 * sidewall_m
    unloaded_radius_m = unloaded_diameter_m / 2.0

    return {
        "section_width_m": section_width_m,
        "aspect_ratio": aspect_pct / 100.0,
        "rim_diameter_m": rim_diameter_m,
        "sidewall_height_m": sidewall_m,
        "unloaded_diameter_m": unloaded_diameter_m,
        "unloaded_radius_m": unloaded_radius_m,
    }


def calc_contact_patch(load_per_tyre_N, tyre_pressure_kPa, section_width_m):
    """
    Estimate tyre contact patch dimensions.
      contact_patch_area   = load_per_tyre (N) / tyre_pressure (Pa)
      contact_patch_length = contact_patch_area / section_width
    These are engineering approximations based on a uniform pressure assumption.
    """
    pressure_Pa = max(tyre_pressure_kPa * 1000.0, 1.0)
    area_m2 = load_per_tyre_N / pressure_Pa
    length_m = area_m2 / max(section_width_m, 0.001)
    return area_m2, length_m


def interp_time_at_speed(speeds_kmh, times_s, target_kmh):
    """
    Linearly interpolate to find the cumulative time at which the vehicle
    first reaches target_kmh.
    Returns None if the target speed was not reached in the simulation.
    """
    if not speeds_kmh:
        return None
    # If the simulation starts at or above the target, return start time
    if speeds_kmh[0] >= target_kmh:
        return times_s[0] if abs(speeds_kmh[0] - target_kmh) < 1e-6 else None
    for i in range(1, len(speeds_kmh)):
        if speeds_kmh[i - 1] < target_kmh <= speeds_kmh[i]:
            frac = (target_kmh - speeds_kmh[i - 1]) / (speeds_kmh[i] - speeds_kmh[i - 1])
            return times_s[i - 1] + frac * (times_s[i] - times_s[i - 1])
    return None  # target not reached


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
peak_power_kW = st.sidebar.number_input(
    "Peak engine power (kW)",
    value=float(vp["peak_power_kW"]),
    min_value=1.0, step=5.0,
    key=f"pp_{vk}",
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
        "Select Gear for Phase 1 Calculation",
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

st.sidebar.subheader("Phase 1 — Operating Condition")
speed_kmh = st.sidebar.number_input(
    "Vehicle speed (km/h)", value=100.0, min_value=0.0, step=5.0
)

# ─── PHASE 1 CALCULATIONS ────────────────────────────────────────────────────────

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

# ─── PHASE 2A — TYRE GEOMETRY & ADJUSTED CRR ─────────────────────────────────────
# These are used by the Phase 2A simulation and the Profile Summary.

# Parse tyre size strings to get unloaded geometry
veh_tyre_geom = parse_tyre_size(vp["tyre_size"])
trl_tyre_geom = parse_tyre_size(tp["tyre_size"])

# Unloaded radii (fall back to loaded radius if parse fails)
veh_unloaded_radius = veh_tyre_geom["unloaded_radius_m"] if veh_tyre_geom else tyre_radius
trl_unloaded_radius = trl_tyre_geom["unloaded_radius_m"] if trl_tyre_geom else trailer_tyre_radius

# Tyre deflection under load
veh_tyre_deflection = max(0.0, veh_unloaded_radius - tyre_radius)
trl_tyre_deflection = max(0.0, trl_unloaded_radius - trailer_tyre_radius)

# Contact patch calculations
veh_section_width = veh_tyre_geom["section_width_m"] if veh_tyre_geom else 0.265
trl_section_width = trl_tyre_geom["section_width_m"] if trl_tyre_geom else 0.235

veh_cp_area, veh_cp_length = calc_contact_patch(
    avg_vehicle_load_per_tyre_N, vehicle_tyre_pressure, veh_section_width
)
trl_cp_area, trl_cp_length = calc_contact_patch(
    avg_trailer_load_per_tyre_N, trailer_tyre_pressure, trl_section_width
)

# Phase 2A adjusted Crr (loaded-radius correction applied)
Crr_veh_p2 = calc_crr_p2(vehicle_tyre_type, tyre_radius, veh_unloaded_radius)
Crr_trl_p2 = calc_crr_p2(trailer_tyre_type, trailer_tyre_radius, trl_unloaded_radius)

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
        st.write(f"Unloaded tyre radius: {veh_unloaded_radius:.3f} m")
        st.write(f"Loaded tyre radius: {tyre_radius:.3f} m")
        st.write(f"Tyre deflection: {veh_tyre_deflection*1000:.1f} mm")
        st.write(f"Avg vehicle load per tyre: {avg_vehicle_load_per_tyre_N:,.0f} N  ({avg_vehicle_load_per_tyre_N/1000:.2f} kN)")
        st.write(f"Contact patch area: {veh_cp_area*10000:.1f} cm²  |  length: {veh_cp_length*100:.1f} cm")
        st.write(f"Phase 1 Crr (pressure-corrected): {Crr_vehicle:.5f}")
        st.write(f"Phase 2A Crr (loaded-radius-corrected): {Crr_veh_p2:.5f}")
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
        st.write(f"Trailer frontal area: {A_trailer:.2f} m²  ({frontal_width:.2f} m × {frontal_height:.2f} m)")
        st.write(f"Tyre type: {trailer_tyre_type}")
        st.write(f"Tyre pressure: {trailer_tyre_pressure:.0f} kPa")
        st.write(f"Unloaded tyre radius: {trl_unloaded_radius:.3f} m")
        st.write(f"Loaded tyre radius: {trailer_tyre_radius:.3f} m")
        st.write(f"Tyre deflection: {trl_tyre_deflection*1000:.1f} mm")
        st.write(f"Avg trailer load per tyre: {avg_trailer_load_per_tyre_N:,.0f} N  ({avg_trailer_load_per_tyre_N/1000:.2f} kN)")
        st.write(f"Contact patch area: {trl_cp_area*10000:.1f} cm²  |  length: {trl_cp_length*100:.1f} cm")
        st.write(f"Phase 1 Crr (pressure-corrected): {Crr_trailer:.5f}")
        st.write(f"Phase 2A Crr (loaded-radius-corrected): {Crr_trl_p2:.5f}")

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

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2A — PREDICTED LEVEL ROAD ACCELERATION
# ═══════════════════════════════════════════════════════════════════════════════

st.divider()
st.header("Phase 2A — Predicted Level Road Acceleration")
st.markdown(
    """
    Simulates the level-road acceleration of the selected vehicle and trailer combination
    using a stepped-speed Euler integration. At each speed step the gear giving the highest
    available tractive force is selected automatically. Results are compared against
    standard level-road acceleration test targets.

    **Assumptions:** flat level road · no wind · no gradient · constant peak torque and power
    (no torque-curve mapping). Aero drag basic (no yaw, no wind).
    """
)

# ── Simulation Inputs ─────────────────────────────────────────────────────────

col_a, col_b, col_c = st.columns(3)
sim_start_kmh = col_a.number_input(
    "Start speed (km/h)", value=0.0, min_value=0.0, step=1.0, key="sim_start"
)
sim_target_kmh = col_b.number_input(
    "Target speed (km/h)", value=96.6, min_value=1.0, step=1.0, key="sim_target"
)
sim_step_kmh = col_c.number_input(
    "Speed step (km/h)", value=0.5, min_value=0.01, max_value=5.0, step=0.1,
    format="%.2f", key="sim_step"
)

# ── Phase 2A Rolling Resistance ───────────────────────────────────────────────
# Uses loaded-radius-corrected Crr (Crr_veh_p2, Crr_trl_p2) already computed above.
# Vehicle: F_rr_veh_p2 = Crr_veh_p2 × m_vehicle × g
# Trailer: F_rr_trl_p2 = Crr_trl_p2 × trailer_tyre_supported_mass × g
#   (only the mass carried on the trailer tyres, excluding tow ball load)
F_rr_veh_p2 = Crr_veh_p2 * m_vehicle * g
F_rr_trl_p2 = Crr_trl_p2 * trailer_tyre_supported_mass * g

# Peak engine power in watts
P_watts = peak_power_kW * 1000.0

# Gear ratios list to evaluate at each speed step
sim_gear_ratios = vp["gear_ratios"]  # use profile's full gear list

# ── Build Speed Array ─────────────────────────────────────────────────────────
# Generate evenly spaced speed steps from start to target.
# Include the exact target speed even if it does not fall on a step boundary.
n_steps = math.ceil((sim_target_kmh - sim_start_kmh) / sim_step_kmh)
sim_speeds_kmh = [sim_start_kmh + i * sim_step_kmh for i in range(n_steps + 1)]
# Clamp to target and ensure target is the last point
sim_speeds_kmh = [s for s in sim_speeds_kmh if s <= sim_target_kmh + 1e-9]
if not sim_speeds_kmh or abs(sim_speeds_kmh[-1] - sim_target_kmh) > 1e-6:
    sim_speeds_kmh.append(sim_target_kmh)

# ── Acceleration Simulation Loop ──────────────────────────────────────────────
sim_rows = []          # detailed table data
sim_speed_out = []     # speed at each recorded point (km/h)
sim_time_out = []      # cumulative time to reach each recorded speed (s)
sim_stopped = False    # True if a ≤ 0 before target was reached

cumulative_time = 0.0

for idx, v_kmh in enumerate(sim_speeds_kmh):

    # 1. Convert speed to m/s
    V_mps = v_kmh / 3.6

    # 2. Aerodynamic drag at this speed (flat road, no wind)
    F_aero_veh = 0.5 * air_density * Cd_vehicle * A_vehicle * V_mps ** 2
    F_aero_trl = 0.5 * air_density * Cd_trailer * A_trailer * V_mps ** 2

    # 3. Rolling resistance (constant — speed-independent for this model)
    F_rr_veh = F_rr_veh_p2
    F_rr_trl = F_rr_trl_p2

    # 4. Total resistance
    F_res = F_rr_veh + F_rr_trl + F_aero_veh + F_aero_trl

    # 5. Find the gear that delivers the highest available tractive force.
    #    For each gear:
    #      T_wheel  = T_engine × gear_ratio × final_drive_ratio × driveline_efficiency
    #      F_torque = T_wheel / loaded_tyre_radius   (torque-limited tractive force)
    #      F_power  = P_watts / max(V_mps, 1.0)      (power-limited tractive force)
    #      F_avail  = min(F_torque, F_power)
    #    Select the gear with the highest F_avail.
    best_F_avail = -1.0
    best_gear_num = 1

    for gi, gr in enumerate(sim_gear_ratios):
        T_whl = T_engine * gr * final_drive_ratio * driveline_efficiency
        F_torque_g = T_whl / tyre_radius
        F_power_g = P_watts / max(V_mps, 1.0)
        F_avail_g = min(F_torque_g, F_power_g)
        if F_avail_g > best_F_avail:
            best_F_avail = F_avail_g
            best_gear_num = gi + 1  # 1-indexed gear number

    # 6. Net force and acceleration
    F_net_sim = best_F_avail - F_res
    a_sim = F_net_sim / m_total

    # 7. Record this speed point with its arrival time
    sim_speed_out.append(v_kmh)
    sim_time_out.append(cumulative_time)
    sim_rows.append({
        "Speed (km/h)": round(v_kmh, 2),
        "Gear": best_gear_num,
        "F_available (N)": round(best_F_avail, 1),
        "F_rr Vehicle (N)": round(F_rr_veh, 1),
        "F_rr Trailer (N)": round(F_rr_trl, 1),
        "F_aero Vehicle (N)": round(F_aero_veh, 1),
        "F_aero Trailer (N)": round(F_aero_trl, 1),
        "F_resistance (N)": round(F_res, 1),
        "F_net (N)": round(F_net_sim, 1),
        "Acceleration (m/s²)": round(a_sim, 4),
        "Cumulative Time (s)": round(cumulative_time, 3),
    })

    # 8. If acceleration ≤ 0, vehicle cannot reach higher speeds — stop simulation
    if a_sim <= 0:
        sim_stopped = True
        break

    # 9. Time increment to reach the next speed step
    #    dt = dV (m/s) / a (m/s²)  →  time to traverse this speed band
    if idx < len(sim_speeds_kmh) - 1:
        next_v = sim_speeds_kmh[idx + 1]
        dV_mps = (next_v - v_kmh) / 3.6
        dt = dV_mps / a_sim
        cumulative_time += dt

# ── Milestone Time Interpolation ──────────────────────────────────────────────
# Test targets reference IVM (in-vehicle measurement) from 0 km/h.
# Interpolate to find exact crossing times.
T_48 = interp_time_at_speed(sim_speed_out, sim_time_out, 48.3)
T_64 = interp_time_at_speed(sim_speed_out, sim_time_out, 64.4)
T_96 = interp_time_at_speed(sim_speed_out, sim_time_out, 96.6)

# 64.4→96.6 km/h window time (subtract crossing times)
if T_64 is not None and T_96 is not None:
    T_64_96 = T_96 - T_64
else:
    T_64_96 = None

# ── PASS/FAIL Evaluation ──────────────────────────────────────────────────────
# Standard level-road acceleration targets:
#   IVM to  48.3 km/h ≤ 12 s
#   IVM to  96.6 km/h ≤ 30 s
#   64.4 to 96.6 km/h ≤ 18 s

def fmt_time(t):
    return f"{t:.2f} s" if t is not None else "Not reached"

def pf(t, limit):
    if t is None:
        return "❌ FAIL"
    return "✅ PASS" if t <= limit else "❌ FAIL"

overall_pass = (
    T_48 is not None and T_48 <= 12
    and T_96 is not None and T_96 <= 30
    and T_64_96 is not None and T_64_96 <= 18
)

# ── Metric Cards ──────────────────────────────────────────────────────────────

if sim_stopped and (T_96 is None):
    top_speed = sim_speed_out[-1] if sim_speed_out else 0
    st.warning(
        f"Simulation stopped at {top_speed:.1f} km/h — net force reached zero "
        "before the target speed. Vehicle cannot reach the target under these conditions."
    )

col1, col2, col3, col4 = st.columns(4)
col1.metric("Time — IVM to 48.3 km/h", fmt_time(T_48), delta="Limit: 12 s", delta_color="off")
col2.metric("Time — IVM to 96.6 km/h", fmt_time(T_96), delta="Limit: 30 s", delta_color="off")
col3.metric("Time — 64.4 to 96.6 km/h", fmt_time(T_64_96), delta="Limit: 18 s", delta_color="off")
col4.metric("Overall Result", "✅ PASS" if overall_pass else "❌ FAIL")

# ── PASS/FAIL Table ───────────────────────────────────────────────────────────

st.subheader("Acceleration Test Results")

pf_data = {
    "Test Target": [
        "IVM to 48.3 km/h",
        "IVM to 96.6 km/h",
        "64.4 to 96.6 km/h",
    ],
    "Predicted Time": [fmt_time(T_48), fmt_time(T_96), fmt_time(T_64_96)],
    "Limit (s)": [12, 30, 18],
    "Pass / Fail": [pf(T_48, 12), pf(T_96, 30), pf(T_64_96, 18)],
}
df_pf = pd.DataFrame(pf_data)
st.dataframe(df_pf, use_container_width=True, hide_index=True)

# ── Four Plots ────────────────────────────────────────────────────────────────

if len(sim_rows) > 1:
    df_sim = pd.DataFrame(sim_rows)

    col_left, col_right = st.columns(2)

    # Plot 1: Speed vs Cumulative Time
    with col_left:
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.plot(
            df_sim["Cumulative Time (s)"],
            df_sim["Speed (km/h)"],
            color="#1976D2", linewidth=2,
        )
        # Mark standard test milestones
        for target_kmh, target_s, label in [
            (48.3, 12, "48.3 km/h / 12 s"),
            (96.6, 30, "96.6 km/h / 30 s"),
        ]:
            ax1.axhline(target_kmh, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
            ax1.axvline(target_s, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
        if T_48 is not None:
            ax1.plot(T_48, 48.3, "o", color="#E64A19", zorder=5)
            ax1.annotate(f"{T_48:.1f} s", (T_48, 48.3), textcoords="offset points",
                         xytext=(6, -12), fontsize=8, color="#E64A19")
        if T_96 is not None:
            ax1.plot(T_96, 96.6, "o", color="#E64A19", zorder=5)
            ax1.annotate(f"{T_96:.1f} s", (T_96, 96.6), textcoords="offset points",
                         xytext=(6, -12), fontsize=8, color="#E64A19")
        ax1.set_xlabel("Time (s)", fontsize=10)
        ax1.set_ylabel("Speed (km/h)", fontsize=10)
        ax1.set_title("Speed vs Time", fontsize=11, fontweight="bold")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

    # Plot 2: Acceleration vs Speed
    with col_right:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(
            df_sim["Speed (km/h)"],
            df_sim["Acceleration (m/s²)"],
            color="#388E3C", linewidth=2,
        )
        ax2.axhline(0, color="red", linestyle="--", linewidth=0.8)
        ax2.set_xlabel("Speed (km/h)", fontsize=10)
        ax2.set_ylabel("Acceleration (m/s²)", fontsize=10)
        ax2.set_title("Acceleration vs Speed", fontsize=11, fontweight="bold")
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # Plot 3: Available Tractive Force vs Speed
    with col_left:
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.plot(
            df_sim["Speed (km/h)"],
            df_sim["F_available (N)"],
            color="#7B1FA2", linewidth=2, label="F available (best gear)",
        )
        ax3.plot(
            df_sim["Speed (km/h)"],
            df_sim["F_resistance (N)"],
            color="#E64A19", linewidth=2, linestyle="--", label="F resistance",
        )
        ax3.set_xlabel("Speed (km/h)", fontsize=10)
        ax3.set_ylabel("Force (N)", fontsize=10)
        ax3.set_title("Tractive Force vs Speed", fontsize=11, fontweight="bold")
        ax3.legend(fontsize=8)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    # Plot 4: Selected Gear vs Speed
    with col_right:
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        ax4.step(
            df_sim["Speed (km/h)"],
            df_sim["Gear"],
            color="#0288D1", linewidth=2, where="post",
        )
        ax4.set_xlabel("Speed (km/h)", fontsize=10)
        ax4.set_ylabel("Gear", fontsize=10)
        ax4.set_yticks(range(1, len(sim_gear_ratios) + 1))
        ax4.set_title("Selected Gear vs Speed", fontsize=11, fontweight="bold")
        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

    # ── Expandable Simulation Table ───────────────────────────────────────────

    with st.expander("Simulation Data Table", expanded=False):
        st.caption(
            "Step-by-step simulation output. Each row shows conditions at the start of "
            "that speed band. Cumulative time is the time elapsed to reach that speed."
        )
        st.dataframe(df_sim, use_container_width=True, hide_index=True)

else:
    st.info("Increase the simulation speed range (target > start) to run the acceleration simulation.")

