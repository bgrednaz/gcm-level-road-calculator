import re
import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="GCM Level Road Calculator", layout="wide")

# ─── VEHICLE PROFILES ────────────────────────────────────────────────────────────
# Each profile contains:
#   idle_rpm      — engine idle speed (RPM); engine will not drop below this
#   redline_rpm   — maximum engine speed (RPM); gear is invalid if RPM exceeds this
#   torque_curve  — list of (RPM, torque_Nm) tuples defining the engine torque curve
#                   Interpolated at the operating RPM; clamped to endpoints if outside.
#   peak_power_kW — hard power cap applied after torque interpolation

vehicle_profiles = {
    "Test Vehicle 1": {
        "vehicle_mass": 3500.0,
        "rated_GCM": 8000.0,
        "peak_torque_Nm": 400.0,
        "peak_power_kW": 200.0,
        "idle_rpm": 800,
        "redline_rpm": 4500,
        "torque_curve": [
            (800,  220),
            (1000, 250),
            (1500, 350),
            (2000, 400),
            (2500, 400),
            (3000, 380),
            (3500, 350),
            (4000, 320),
            (4500, 280),
        ],
        "final_drive_ratio": 3.70,
        "driveline_efficiency": 0.88,
        "tyre_size": "265/65R17",
        "tyre_radius": 0.380,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "Highway",
        "Cd": 0.40,
        "frontal_area": 3.50,
        "gear_ratios": [4.71, 3.14, 2.11, 1.67, 1.29, 1.00, 0.84, 0.67, 0.60, 0.52],
    },
    "Medium Dual Cab 4WD": {
        "vehicle_mass": 2200.0,
        "rated_GCM": 6000.0,
        "peak_torque_Nm": 500.0,
        "peak_power_kW": 150.0,
        "idle_rpm": 750,
        "redline_rpm": 3800,
        "torque_curve": [
            (750,  250),
            (1200, 420),
            (1600, 500),
            (2000, 500),
            (2400, 480),
            (2800, 440),
            (3200, 380),
            (3800, 300),
        ],
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
        "idle_rpm": 750,
        "redline_rpm": 3800,
        "torque_curve": [
            (750,  320),
            (1200, 550),
            (1600, 650),
            (2000, 650),
            (2400, 620),
            (2800, 580),
            (3200, 480),
            (3800, 370),
        ],
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
        "idle_rpm": 600,
        "redline_rpm": 5500,
        "torque_curve": [
            (600,  280),
            (1200, 430),
            (1800, 570),
            (2400, 600),
            (3000, 590),
            (3600, 560),
            (4200, 500),
            (5000, 400),
            (5500, 340),
        ],
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
        "idle_rpm": 750,
        "redline_rpm": 4000,
        "torque_curve": [
            (750,  300),
            (1200, 500),
            (1600, 650),
            (2000, 650),
            (2400, 630),
            (2800, 580),
            (3200, 480),
            (4000, 360),
        ],
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
        "idle_rpm": 800,
        "redline_rpm": 4500,
        "torque_curve": [
            (800,  200),
            (1500, 350),
            (2000, 400),
            (2500, 400),
            (3000, 380),
            (3500, 350),
            (4000, 300),
            (4500, 250),
        ],
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

# Phase 1 Crr base values (pressure-corrected)
BASE_CRR_P1 = {"Highway": 0.0075, "All-Terrain": 0.011, "Mud-Terrain": 0.015}
REF_PRESSURE_KPA = 280.0

def estimate_crr(tyre_type, tyre_pressure_kpa):
    """Phase 1: Crr from tyre type and pressure. Reference pressure 280 kPa."""
    base = BASE_CRR_P1.get(tyre_type, 0.010)
    pressure_factor = (REF_PRESSURE_KPA / max(tyre_pressure_kpa, 50.0)) ** 0.5
    return round(base * pressure_factor, 5)


# Phase 2A Crr base values (with loaded-radius correction)
BASE_CRR_P2 = {"Highway": 0.010, "All-Terrain": 0.013, "Mud-Terrain": 0.017}

def calc_crr_p2(tyre_type, loaded_radius_m, unloaded_radius_m):
    """
    Phase 2A: Crr_adjusted = Crr_base × (1 + 2.5 × max(0, 1 − loaded/unloaded)).
    Higher deflection (lower loaded_radius_ratio) increases Crr.
    """
    base = BASE_CRR_P2.get(tyre_type, 0.012)
    if unloaded_radius_m <= 0:
        return base
    ratio = loaded_radius_m / unloaded_radius_m
    return base * (1.0 + 2.5 * max(0.0, 1.0 - ratio))


def parse_tyre_size(tyre_str):
    """
    Parse "265/65R17" → section_width_m, sidewall_height_m, rim_diameter_m,
    unloaded_diameter_m, unloaded_radius_m.  Returns None if unparseable.
    """
    match = re.match(r"(\d+)/(\d+)[Rr](\d+(?:\.\d+)?)", tyre_str.strip())
    if not match:
        return None
    width_mm = float(match.group(1))
    aspect_pct = float(match.group(2))
    rim_in = float(match.group(3))

    sw_m = width_mm / 1000.0
    sh_m = sw_m * (aspect_pct / 100.0)
    rd_m = rim_in * 0.0254
    ud_m = rd_m + 2.0 * sh_m
    return {
        "section_width_m": sw_m,
        "aspect_ratio": aspect_pct / 100.0,
        "rim_diameter_m": rd_m,
        "sidewall_height_m": sh_m,
        "unloaded_diameter_m": ud_m,
        "unloaded_radius_m": ud_m / 2.0,
    }


def calc_contact_patch(load_N, pressure_kPa, section_width_m):
    """
    Contact patch area  = load / pressure  (uniform pressure assumption).
    Contact patch length = area / section_width.
    Engineering estimates only.
    """
    p_Pa = max(pressure_kPa * 1000.0, 1.0)
    area = load_N / p_Pa
    length = area / max(section_width_m, 0.001)
    return area, length


def interp_torque(torque_curve, rpm):
    """
    Linearly interpolate engine torque from the torque curve at the given RPM.
    Clamps to the first/last point if RPM is outside the curve range.
    torque_curve: list of (rpm, torque_Nm) tuples, sorted ascending by RPM.
    """
    if not torque_curve:
        return None
    rpms    = [p[0] for p in torque_curve]
    torques = [p[1] for p in torque_curve]
    if rpm <= rpms[0]:
        return torques[0]
    if rpm >= rpms[-1]:
        return torques[-1]
    for i in range(1, len(rpms)):
        if rpms[i - 1] <= rpm <= rpms[i]:
            frac = (rpm - rpms[i - 1]) / (rpms[i] - rpms[i - 1])
            return torques[i - 1] + frac * (torques[i] - torques[i - 1])
    return torques[-1]


def select_best_gear(
    gear_ratios, final_drive_ratio, driveline_efficiency,
    tyre_radius_m, idle_rpm, redline_rpm, torque_curve,
    peak_power_W, V_mps, fallback_torque_Nm=400.0,
):
    """
    Evaluate every gear at the given vehicle speed and select the one
    that delivers the highest available tractive force.

    For each gear:
      1. wheel_speed_rad_s = V_mps / tyre_radius_m
      2. engine_rpm_calc   = wheel_speed × gear_ratio × final_drive × 60 / 2π
      3. effective_rpm     = max(engine_rpm_calc, idle_rpm)   ← floor at idle
      4. If effective_rpm > redline_rpm → gear marked INVALID
      5. torque_at_rpm     = interpolated from curve (or fallback constant)
      6. P_engine          = torque × effective_rpm × 2π / 60
      7. P_capped          = min(P_engine, peak_power_W)
      8. T_wheel           = torque × gear_ratio × final_drive × driveline_eff
      9. F_torque          = T_wheel / tyre_radius
     10. F_power           = P_capped / max(V_mps, 1.0)
     11. F_available       = min(F_torque, F_power)

    Returns:
      gear_rows  — list of dicts, one per gear, with full calculation detail
      best_idx   — index of selected gear (highest F_available among valid gears),
                   or None if no gear is valid
    """
    TWO_PI = 2.0 * math.pi
    wheel_rad_s = V_mps / max(tyre_radius_m, 0.001)

    gear_rows = []
    best_idx = None
    best_F = -1.0

    for gi, gr in enumerate(gear_ratios):
        # Engine speed at this road speed and gear
        rpm_calc = wheel_rad_s * gr * final_drive_ratio * 60.0 / TWO_PI

        # Clamp to idle — engine doesn't stall at low road speed (launch scenario)
        effective_rpm = max(rpm_calc, float(idle_rpm))

        # Gear is invalid above redline
        valid = effective_rpm <= redline_rpm

        if valid:
            if torque_curve:
                torque_Nm = interp_torque(torque_curve, effective_rpm)
            else:
                torque_Nm = fallback_torque_Nm  # constant peak torque fallback

            # Engine power from torque and RPM, then cap at peak power
            P_calc = torque_Nm * effective_rpm * TWO_PI / 60.0
            P_capped = min(P_calc, peak_power_W)

            # Wheel torque through gearbox and final drive
            T_wheel = torque_Nm * gr * final_drive_ratio * driveline_efficiency

            # Tractive force limited by torque, then by power
            F_torque = T_wheel / max(tyre_radius_m, 0.001)
            F_power  = P_capped / max(V_mps, 1.0)
            F_avail  = min(F_torque, F_power)
        else:
            torque_Nm = None
            P_calc = P_capped = None
            T_wheel = F_torque = F_power = F_avail = None

        row = {
            "Gear":               gi + 1,
            "Gear Ratio":         round(gr, 3),
            "Calc RPM":           round(rpm_calc, 0),
            "Effective RPM":      round(effective_rpm, 0),
            "Torque at RPM (Nm)": round(torque_Nm, 1)       if torque_Nm  is not None else None,
            "Engine Power (W)":   round(P_calc, 0)           if P_calc     is not None else None,
            "Capped Power (W)":   round(P_capped, 0)         if P_capped   is not None else None,
            "F_torque (N)":       round(F_torque, 1)         if F_torque   is not None else None,
            "F_power (N)":        round(F_power, 1)          if F_power    is not None else None,
            "F_available (N)":    round(F_avail, 1)          if F_avail    is not None else None,
            "Valid":              valid,
            "Selected":           False,
        }
        gear_rows.append(row)

        if valid and F_avail is not None and F_avail > best_F:
            best_F = F_avail
            best_idx = gi

    if best_idx is not None:
        gear_rows[best_idx]["Selected"] = True

    return gear_rows, best_idx


def interp_time_at_speed(speeds_kmh, times_s, target_kmh):
    """
    Linearly interpolate the cumulative time at which the vehicle first
    reaches target_kmh.  Returns None if the speed was not reached.
    """
    if not speeds_kmh:
        return None
    if speeds_kmh[0] >= target_kmh:
        return times_s[0] if abs(speeds_kmh[0] - target_kmh) < 1e-6 else None
    for i in range(1, len(speeds_kmh)):
        if speeds_kmh[i - 1] < target_kmh <= speeds_kmh[i]:
            frac = (target_kmh - speeds_kmh[i - 1]) / (speeds_kmh[i] - speeds_kmh[i - 1])
            return times_s[i - 1] + frac * (times_s[i] - times_s[i - 1])
    return None


# ─── CONSTANTS ───────────────────────────────────────────────────────────────────

g = 9.81  # m/s²

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────

st.sidebar.header("Inputs")

# ── Vehicle Profile ──────────────────────────────────────────────────────────────

st.sidebar.subheader("Vehicle Profile")

selected_vehicle = st.sidebar.selectbox(
    "Select Vehicle Profile", list(vehicle_profiles.keys())
)
vp = vehicle_profiles[selected_vehicle]
vk = selected_vehicle  # widget key prefix

m_vehicle = st.sidebar.number_input(
    "Vehicle mass (kg)", value=float(vp["vehicle_mass"]),
    min_value=0.0, step=50.0, key=f"m_vehicle_{vk}",
)
GCM = st.sidebar.number_input(
    "Rated GCM (kg)", value=float(vp["rated_GCM"]),
    min_value=1.0, step=100.0, key=f"gcm_{vk}",
)
peak_power_kW = st.sidebar.number_input(
    "Peak engine power (kW)", value=float(vp["peak_power_kW"]),
    min_value=1.0, step=5.0, key=f"pp_{vk}",
)
final_drive_ratio = st.sidebar.number_input(
    "Final drive ratio", value=float(vp["final_drive_ratio"]),
    min_value=0.01, step=0.01, format="%.3f", key=f"fdr_{vk}",
)
driveline_efficiency = st.sidebar.number_input(
    "Driveline efficiency (0-1)", value=float(vp["driveline_efficiency"]),
    min_value=0.0, max_value=1.0, step=0.01, format="%.2f", key=f"de_{vk}",
)
tyre_radius = st.sidebar.number_input(
    "Loaded tyre radius (m)", value=float(vp["tyre_radius"]),
    min_value=0.01, step=0.005, format="%.3f", key=f"vtr_{vk}",
)
num_vehicle_tyres = int(st.sidebar.number_input(
    "Tyres carrying load", value=int(vp["num_vehicle_tyres"]),
    min_value=1, step=1, key=f"nvt_{vk}",
))
vehicle_tyre_pressure = st.sidebar.number_input(
    "Tyre pressure (kPa)", value=float(vp["tyre_pressure_kPa"]),
    min_value=50.0, step=10.0, key=f"vtp_{vk}",
)
vehicle_tyre_type = st.sidebar.selectbox(
    "Tyre type", TYRE_TYPES,
    index=TYRE_TYPES.index(vp["tyre_type"]), key=f"vtt_{vk}",
)
Cd_vehicle = st.sidebar.number_input(
    "Vehicle Cd", value=float(vp["Cd"]),
    min_value=0.0, step=0.01, format="%.2f", key=f"cdv_{vk}",
)
A_vehicle = st.sidebar.number_input(
    "Vehicle frontal area (m2)", value=float(vp["frontal_area"]),
    min_value=0.1, step=0.1, format="%.2f", key=f"afv_{vk}",
)

st.sidebar.divider()

# ── Trailer Profile ───────────────────────────────────────────────────────────────

st.sidebar.subheader("Fixed Dual-Axle Trailer Profile")

selected_trailer = st.sidebar.selectbox(
    "Select Trailer Profile", list(trailer_profiles.keys())
)
tp = trailer_profiles[selected_trailer]
tk = selected_trailer

m_trailer = st.sidebar.number_input(
    "Trailer mass (kg)", value=float(tp["trailer_mass"]),
    min_value=0.0, step=50.0, key=f"tm_{tk}",
)
tow_ball_mass = st.sidebar.number_input(
    "Tow ball mass (kg)", value=float(tp["tow_ball_mass"]),
    min_value=0.0, step=10.0, key=f"tbm_{tk}",
)
num_trailer_tyres = int(st.sidebar.number_input(
    "Number of trailer tyres", value=int(tp["num_tyres"]),
    min_value=1, step=1, key=f"ntt_{tk}",
))
trailer_tyre_pressure = st.sidebar.number_input(
    "Trailer tyre pressure (kPa)", value=float(tp["tyre_pressure_kPa"]),
    min_value=50.0, step=10.0, key=f"ttp_{tk}",
)
trailer_tyre_type = st.sidebar.selectbox(
    "Trailer tyre type", TYRE_TYPES,
    index=TYRE_TYPES.index(tp["tyre_type"]), key=f"ttt_{tk}",
)
trailer_tyre_radius = st.sidebar.number_input(
    "Trailer loaded tyre radius (m)", value=float(tp["tyre_radius"]),
    min_value=0.01, step=0.005, format="%.3f", key=f"ttr_{tk}",
)
Cd_trailer = st.sidebar.number_input(
    "Trailer Cd", value=float(tp["Cd"]),
    min_value=0.0, step=0.01, format="%.2f", key=f"cdt_{tk}",
)
frontal_width = st.sidebar.number_input(
    "Trailer frontal width (m)", value=float(tp["frontal_width"]),
    min_value=0.1, step=0.05, format="%.2f", key=f"fw_{tk}",
)
frontal_height = st.sidebar.number_input(
    "Trailer frontal height (m)", value=float(tp["frontal_height"]),
    min_value=0.1, step=0.05, format="%.2f", key=f"fh_{tk}",
)

A_trailer_calc = frontal_width * frontal_height
override_area = st.sidebar.checkbox(
    "Override trailer frontal area", value=False, key=f"oa_{tk}"
)
if override_area:
    A_trailer = st.sidebar.number_input(
        "Trailer frontal area override (m2)", value=round(A_trailer_calc, 2),
        min_value=0.1, step=0.05, format="%.2f", key=f"aft_ov_{tk}",
    )
else:
    A_trailer = A_trailer_calc
    st.sidebar.caption(f"Trailer frontal area (w × h): {A_trailer:.2f} m²")

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

V = speed_kmh / 3.6  # m/s

# Mass
m_total        = m_vehicle + m_trailer
GCM_utilisation = (m_total / GCM) * 100

# Rolling resistance (Phase 1 pressure-corrected Crr)
Crr_vehicle = estimate_crr(vehicle_tyre_type, vehicle_tyre_pressure)
Crr_trailer = estimate_crr(trailer_tyre_type, trailer_tyre_pressure)

# Tyre loads
avg_vehicle_load_per_tyre_N  = (m_vehicle * g) / num_vehicle_tyres
trailer_tyre_supported_mass  = max(0.0, m_trailer - tow_ball_mass)
avg_trailer_load_per_tyre_N  = (trailer_tyre_supported_mass * g) / num_trailer_tyres

# Rolling resistance forces
F_rr_vehicle = Crr_vehicle * m_vehicle * g
F_rr_trailer = Crr_trailer * m_trailer * g

# Aerodynamic drag
F_aero_vehicle = 0.5 * air_density * Cd_vehicle * A_vehicle * V ** 2
F_aero_trailer = 0.5 * air_density * Cd_trailer * A_trailer * V ** 2

# Total resistance
F_resistance_total = F_rr_vehicle + F_rr_trailer + F_aero_vehicle + F_aero_trailer

# ── Automatic Gear Selection (RPM + Torque Curve) ────────────────────────────────
# Evaluate every gear at the operating speed and choose the one with
# the highest available tractive force.

P_watts_p1 = peak_power_kW * 1000.0

gear_rows_p1, best_idx_p1 = select_best_gear(
    gear_ratios        = vp["gear_ratios"],
    final_drive_ratio  = final_drive_ratio,
    driveline_efficiency = driveline_efficiency,
    tyre_radius_m      = tyre_radius,
    idle_rpm           = vp["idle_rpm"],
    redline_rpm        = vp["redline_rpm"],
    torque_curve       = vp.get("torque_curve"),
    peak_power_W       = P_watts_p1,
    V_mps              = V,
    fallback_torque_Nm = vp["peak_torque_Nm"],
)

if best_idx_p1 is not None:
    best_p1 = gear_rows_p1[best_idx_p1]
    p1_gear_num    = best_p1["Gear"]
    p1_gear_ratio  = best_p1["Gear Ratio"]
    p1_engine_rpm  = best_p1["Effective RPM"]
    p1_torque_Nm   = best_p1["Torque at RPM (Nm)"]
    p1_power_W     = best_p1["Capped Power (W)"]
    p1_F_torque    = best_p1["F_torque (N)"]
    p1_F_power     = best_p1["F_power (N)"]
    F_available    = best_p1["F_available (N)"]
    # Wheel torque at selected gear
    T_wheel        = (p1_torque_Nm * p1_gear_ratio
                      * final_drive_ratio * driveline_efficiency)
else:
    # No valid gear (e.g. all gears above redline at this speed)
    p1_gear_num   = None
    p1_gear_ratio = None
    p1_engine_rpm = None
    p1_torque_Nm  = None
    p1_power_W    = None
    p1_F_torque   = None
    p1_F_power    = None
    F_available   = 0.0
    T_wheel       = 0.0

# Net tractive force and acceleration
F_net = F_available - F_resistance_total
a     = F_net / m_total if m_total > 0 else 0.0

# Hitch force
F_hitch = m_trailer * a + F_rr_trailer + F_aero_trailer

# ─── PHASE 2A — TYRE GEOMETRY & ADJUSTED CRR ─────────────────────────────────────

veh_tyre_geom = parse_tyre_size(vp["tyre_size"])
trl_tyre_geom = parse_tyre_size(tp["tyre_size"])

veh_unloaded_radius = (veh_tyre_geom["unloaded_radius_m"]
                       if veh_tyre_geom else tyre_radius)
trl_unloaded_radius = (trl_tyre_geom["unloaded_radius_m"]
                       if trl_tyre_geom else trailer_tyre_radius)

veh_tyre_deflection = max(0.0, veh_unloaded_radius - tyre_radius)
trl_tyre_deflection = max(0.0, trl_unloaded_radius - trailer_tyre_radius)

veh_section_width = (veh_tyre_geom["section_width_m"] if veh_tyre_geom else 0.265)
trl_section_width = (trl_tyre_geom["section_width_m"] if trl_tyre_geom else 0.235)

veh_cp_area, veh_cp_length = calc_contact_patch(
    avg_vehicle_load_per_tyre_N, vehicle_tyre_pressure, veh_section_width
)
trl_cp_area, trl_cp_length = calc_contact_patch(
    avg_trailer_load_per_tyre_N, trailer_tyre_pressure, trl_section_width
)

Crr_veh_p2 = calc_crr_p2(vehicle_tyre_type, tyre_radius, veh_unloaded_radius)
Crr_trl_p2 = calc_crr_p2(trailer_tyre_type, trailer_tyre_radius, trl_unloaded_radius)

# ─── MAIN AREA ───────────────────────────────────────────────────────────────────

st.title("GCM Level Road Calculator")
st.markdown(
    """
    **Phase 1 — Level Road Steady-State Calculator.**
    Estimates towing performance for a vehicle and trailer on a flat, level road
    at a single selected speed. Gear is selected automatically from the vehicle
    profile using engine RPM and the torque curve. All inputs and outputs use SI units.
    """
)

# Warnings
gcm_exceeded = m_total > GCM
net_negative  = F_net < 0
no_valid_gear = best_idx_p1 is None

if gcm_exceeded:
    st.error(
        f"WARNING: Total combination mass {m_total:,.0f} kg exceeds "
        f"rated GCM of {GCM:,.0f} kg by {m_total - GCM:,.0f} kg."
    )
if no_valid_gear:
    st.error(
        "WARNING: No valid gear found at this speed — all gears exceed the "
        f"redline ({vp['redline_rpm']:,} RPM). Vehicle cannot operate at "
        f"{speed_kmh:.0f} km/h with this profile."
    )
elif net_negative:
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
        st.write(f"Peak power: {peak_power_kW:.0f} kW")
        st.write(f"Idle RPM: {vp['idle_rpm']:,}  |  Redline RPM: {vp['redline_rpm']:,}")
        st.write(f"Vehicle Cd: {Cd_vehicle:.2f}  |  Frontal area: {A_vehicle:.2f} m²")
        st.write(f"Tyre type: {vehicle_tyre_type}  |  Pressure: {vehicle_tyre_pressure:.0f} kPa")
        st.write(f"Unloaded radius: {veh_unloaded_radius:.3f} m  |  Loaded: {tyre_radius:.3f} m  |  Deflection: {veh_tyre_deflection*1000:.1f} mm")
        st.write(f"Avg load/tyre: {avg_vehicle_load_per_tyre_N:,.0f} N  ({avg_vehicle_load_per_tyre_N/1000:.2f} kN)")
        st.write(f"Contact patch: {veh_cp_area*10000:.1f} cm²  ×  {veh_cp_length*100:.1f} cm")
        st.write(f"Phase 1 Crr: {Crr_vehicle:.5f}  |  Phase 2A Crr: {Crr_veh_p2:.5f}")
        st.write(f"Gear ratios: {vp['gear_ratios']}")
        st.write(f"Final drive: {final_drive_ratio:.3f}")
    with col2:
        st.markdown("**Trailer**")
        st.write(f"Profile: {selected_trailer}")
        st.write(f"Tyre size: {tp['tyre_size']}")
        st.write(f"Trailer mass: {m_trailer:,.0f} kg  |  Tow ball: {tow_ball_mass:,.0f} kg")
        st.write(f"Tyre supported mass: {trailer_tyre_supported_mass:,.0f} kg")
        st.write(f"Trailer Cd: {Cd_trailer:.2f}  |  Frontal area: {A_trailer:.2f} m²  ({frontal_width:.2f} × {frontal_height:.2f} m)")
        st.write(f"Tyre type: {trailer_tyre_type}  |  Pressure: {trailer_tyre_pressure:.0f} kPa")
        st.write(f"Unloaded radius: {trl_unloaded_radius:.3f} m  |  Loaded: {trailer_tyre_radius:.3f} m  |  Deflection: {trl_tyre_deflection*1000:.1f} mm")
        st.write(f"Avg load/tyre: {avg_trailer_load_per_tyre_N:,.0f} N  ({avg_trailer_load_per_tyre_N/1000:.2f} kN)")
        st.write(f"Contact patch: {trl_cp_area*10000:.1f} cm²  ×  {trl_cp_length*100:.1f} cm")
        st.write(f"Phase 1 Crr: {Crr_trailer:.5f}  |  Phase 2A Crr: {Crr_trl_p2:.5f}")
    st.markdown("---")
    st.markdown("**Combination**")
    c1, c2, c3 = st.columns(3)
    c1.write(f"Total combination mass: {m_total:,.0f} kg")
    c2.write(f"Rated GCM: {GCM:,.0f} kg")
    c3.write(f"GCM utilisation: {GCM_utilisation:.1f}%")
    st.caption(
        "Rolling resistance is estimated from tyre type, tyre loading, pressure and "
        "loaded-radius correction. Contact patch values are engineering estimates and "
        "are not direct rolling resistance measurements."
    )

# ─── MASS CALCULATIONS ───────────────────────────────────────────────────────────

st.subheader("Mass Calculations")
col1, col2, col3 = st.columns(3)
col1.metric("Total Combination Mass", f"{m_total:,.0f} kg")
col2.metric(
    "GCM Utilisation", f"{GCM_utilisation:.1f}%",
    delta=f"{GCM_utilisation - 100:.1f}% over limit" if gcm_exceeded else None,
    delta_color="inverse",
)
col3.metric("Rated GCM", f"{GCM:,.0f} kg")

# ─── DRIVELINE / TRACTIVE FORCE ──────────────────────────────────────────────────

st.subheader("Driveline / Tractive Force")

def _fmt(v, fmt=","):
    return f"{v:{fmt}}" if v is not None else "N/A"

col1, col2, col3 = st.columns(3)
col1.metric("Auto-Selected Gear",
            f"Gear {p1_gear_num}  (ratio {p1_gear_ratio:.3f})" if p1_gear_num else "N/A")
col2.metric("Engine RPM", f"{int(p1_engine_rpm):,}" if p1_engine_rpm is not None else "N/A")
col3.metric("Torque at RPM", f"{p1_torque_Nm:,.0f} Nm" if p1_torque_Nm is not None else "N/A")

col4, col5, col6 = st.columns(3)
col4.metric("Engine Power (capped)", f"{p1_power_W/1000:.1f} kW" if p1_power_W is not None else "N/A")
col5.metric("Torque-Limited Force", f"{p1_F_torque:,.0f} N" if p1_F_torque is not None else "N/A")
col6.metric("Available Tractive Force", f"{F_available:,.0f} N")

# ─── GEAR SELECTION CHECK ────────────────────────────────────────────────────────

with st.expander("Gear Selection Check", expanded=False):
    st.caption(
        f"All gears evaluated at {speed_kmh:.0f} km/h ({V:.2f} m/s). "
        f"Idle: {vp['idle_rpm']:,} RPM  |  Redline: {vp['redline_rpm']:,} RPM. "
        "Effective RPM = max(calculated RPM, idle RPM). "
        "Gears above redline are marked invalid."
    )
    # Build display DataFrame — replace None with "—" for readability
    display_rows = []
    for row in gear_rows_p1:
        display_rows.append({
            "Gear":               row["Gear"],
            "Ratio":              row["Gear Ratio"],
            "Calc RPM":           int(row["Calc RPM"]),
            "Eff. RPM":           int(row["Effective RPM"]),
            "Torque (Nm)":        f"{row['Torque at RPM (Nm)']:.0f}" if row["Torque at RPM (Nm)"] is not None else "—",
            "Power (kW)":         f"{row['Capped Power (W)']/1000:.1f}" if row["Capped Power (W)"] is not None else "—",
            "F_torque (N)":       f"{row['F_torque (N)']:.0f}" if row["F_torque (N)"] is not None else "—",
            "F_power (N)":        f"{row['F_power (N)']:.0f}" if row["F_power (N)"] is not None else "—",
            "F_available (N)":    f"{row['F_available (N)']:.0f}" if row["F_available (N)"] is not None else "—",
            "Valid":              "✅" if row["Valid"] else "❌ Over redline",
            "Selected":           "★ Selected" if row["Selected"] else "",
        })
    df_gears = pd.DataFrame(display_rows)
    st.dataframe(df_gears, use_container_width=True, hide_index=True)

# ─── PERFORMANCE ─────────────────────────────────────────────────────────────────

st.subheader("Performance")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Force", f"{F_net:,.0f} N")
col2.metric("Acceleration", f"{a:.4f} m/s²")
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
        "Available Tractive Force",
        "Net Force",
        "Hitch Force",
    ],
    "Value (N)": [
        round(F_rr_vehicle, 1),
        round(F_rr_trailer, 1),
        round(F_aero_vehicle, 1),
        round(F_aero_trailer, 1),
        round(F_resistance_total, 1),
        round(F_available, 1),
        round(F_net, 1),
        round(F_hitch, 1),
    ],
    "Value (kN)": [
        round(F_rr_vehicle / 1000, 3),
        round(F_rr_trailer / 1000, 3),
        round(F_aero_vehicle / 1000, 3),
        round(F_aero_trailer / 1000, 3),
        round(F_resistance_total / 1000, 3),
        round(F_available / 1000, 3),
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
        ha="center", va="bottom", fontsize=9, fontweight="bold",
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
    Simulates level-road acceleration using a stepped-speed Euler integration.
    At each speed step the gear giving the highest available tractive force is
    selected automatically using the engine RPM and torque curve.
    Results are compared against standard level-road acceleration test targets.

    **Assumptions:** flat level road · no wind · no gradient · no torque-curve
    smoothing between steps. Aero drag basic (no yaw, no wind).
    """
)

# ── Simulation Inputs ─────────────────────────────────────────────────────────

col_a, col_b, col_c = st.columns(3)
sim_start_kmh  = col_a.number_input("Start speed (km/h)", value=0.0, min_value=0.0, step=1.0, key="sim_start")
sim_target_kmh = col_b.number_input("Target speed (km/h)", value=96.6, min_value=1.0, step=1.0, key="sim_target")
sim_step_kmh   = col_c.number_input("Speed step (km/h)", value=0.5, min_value=0.01, max_value=5.0, step=0.1,
                                     format="%.2f", key="sim_step")

# ── Phase 2A Rolling Resistance ───────────────────────────────────────────────
# Uses loaded-radius-corrected Crr. Trailer RR uses tyre-supported mass only.
F_rr_veh_p2 = Crr_veh_p2 * m_vehicle * g
F_rr_trl_p2 = Crr_trl_p2 * trailer_tyre_supported_mass * g

P_watts_p2a = peak_power_kW * 1000.0

# ── Build Speed Array ─────────────────────────────────────────────────────────
n_steps = math.ceil((sim_target_kmh - sim_start_kmh) / sim_step_kmh)
sim_speeds_kmh = [sim_start_kmh + i * sim_step_kmh for i in range(n_steps + 1)]
sim_speeds_kmh = [s for s in sim_speeds_kmh if s <= sim_target_kmh + 1e-9]
if not sim_speeds_kmh or abs(sim_speeds_kmh[-1] - sim_target_kmh) > 1e-6:
    sim_speeds_kmh.append(sim_target_kmh)

# ── Acceleration Simulation Loop ──────────────────────────────────────────────
sim_rows      = []
sim_speed_out = []
sim_time_out  = []
sim_stopped   = False
cumulative_time = 0.0

for idx, v_kmh in enumerate(sim_speeds_kmh):
    V_mps = v_kmh / 3.6

    # Aerodynamic drag at this speed
    F_aero_veh = 0.5 * air_density * Cd_vehicle * A_vehicle * V_mps ** 2
    F_aero_trl = 0.5 * air_density * Cd_trailer * A_trailer * V_mps ** 2

    # Rolling resistance (speed-independent for this model)
    F_rr_veh = F_rr_veh_p2
    F_rr_trl = F_rr_trl_p2

    F_res = F_rr_veh + F_rr_trl + F_aero_veh + F_aero_trl

    # Select best gear using RPM and torque curve
    g_rows, b_idx = select_best_gear(
        gear_ratios          = vp["gear_ratios"],
        final_drive_ratio    = final_drive_ratio,
        driveline_efficiency = driveline_efficiency,
        tyre_radius_m        = tyre_radius,
        idle_rpm             = vp["idle_rpm"],
        redline_rpm          = vp["redline_rpm"],
        torque_curve         = vp.get("torque_curve"),
        peak_power_W         = P_watts_p2a,
        V_mps                = V_mps,
        fallback_torque_Nm   = vp["peak_torque_Nm"],
    )

    if b_idx is not None:
        best_sim = g_rows[b_idx]
        best_F_avail = best_sim["F_available (N)"]
        best_gear_n  = best_sim["Gear"]
    else:
        best_F_avail = 0.0
        best_gear_n  = None

    F_net_sim = best_F_avail - F_res
    a_sim     = F_net_sim / m_total if m_total > 0 else 0.0

    sim_speed_out.append(v_kmh)
    sim_time_out.append(cumulative_time)
    sim_rows.append({
        "Speed (km/h)":         round(v_kmh, 2),
        "Gear":                 best_gear_n if best_gear_n else "—",
        "F_available (N)":      round(best_F_avail, 1),
        "F_rr Vehicle (N)":     round(F_rr_veh, 1),
        "F_rr Trailer (N)":     round(F_rr_trl, 1),
        "F_aero Vehicle (N)":   round(F_aero_veh, 1),
        "F_aero Trailer (N)":   round(F_aero_trl, 1),
        "F_resistance (N)":     round(F_res, 1),
        "F_net (N)":            round(F_net_sim, 1),
        "Acceleration (m/s²)":  round(a_sim, 4),
        "Cumulative Time (s)":  round(cumulative_time, 3),
    })

    if a_sim <= 0:
        sim_stopped = True
        break

    if idx < len(sim_speeds_kmh) - 1:
        next_v  = sim_speeds_kmh[idx + 1]
        dV_mps  = (next_v - v_kmh) / 3.6
        cumulative_time += dV_mps / a_sim

# ── Milestone Interpolation ───────────────────────────────────────────────────
T_48    = interp_time_at_speed(sim_speed_out, sim_time_out, 48.3)
T_64    = interp_time_at_speed(sim_speed_out, sim_time_out, 64.4)
T_96    = interp_time_at_speed(sim_speed_out, sim_time_out, 96.6)
T_64_96 = (T_96 - T_64) if (T_64 is not None and T_96 is not None) else None

def fmt_time(t):
    return f"{t:.2f} s" if t is not None else "Not reached"

def pf(t, limit):
    if t is None:
        return "❌ FAIL"
    return "✅ PASS" if t <= limit else "❌ FAIL"

overall_pass = (
    T_48    is not None and T_48    <= 12
    and T_96    is not None and T_96    <= 30
    and T_64_96 is not None and T_64_96 <= 18
)

# ── Metric Cards ──────────────────────────────────────────────────────────────

if sim_stopped and T_96 is None:
    top_v = sim_speed_out[-1] if sim_speed_out else 0
    st.warning(
        f"Simulation stopped at {top_v:.1f} km/h — net force reached zero "
        "before the target speed."
    )

col1, col2, col3, col4 = st.columns(4)
col1.metric("Time — IVM to 48.3 km/h",    fmt_time(T_48),    delta="Limit: 12 s", delta_color="off")
col2.metric("Time — IVM to 96.6 km/h",    fmt_time(T_96),    delta="Limit: 30 s", delta_color="off")
col3.metric("Time — 64.4 to 96.6 km/h",   fmt_time(T_64_96), delta="Limit: 18 s", delta_color="off")
col4.metric("Overall Result", "✅ PASS" if overall_pass else "❌ FAIL")

# ── PASS/FAIL Table ───────────────────────────────────────────────────────────

st.subheader("Acceleration Test Results")
pf_data = {
    "Test Target":    ["IVM to 48.3 km/h", "IVM to 96.6 km/h", "64.4 to 96.6 km/h"],
    "Predicted Time": [fmt_time(T_48), fmt_time(T_96), fmt_time(T_64_96)],
    "Limit (s)":      [12, 30, 18],
    "Pass / Fail":    [pf(T_48, 12), pf(T_96, 30), pf(T_64_96, 18)],
}
st.dataframe(pd.DataFrame(pf_data), use_container_width=True, hide_index=True)

# ── Four Plots ────────────────────────────────────────────────────────────────

if len(sim_rows) > 1:
    df_sim = pd.DataFrame(sim_rows)

    col_left, col_right = st.columns(2)

    # Plot 1 — Speed vs Time
    with col_left:
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.plot(df_sim["Cumulative Time (s)"], df_sim["Speed (km/h)"],
                 color="#1976D2", linewidth=2)
        for tgt_kmh, tgt_s in [(48.3, 12), (96.6, 30)]:
            ax1.axhline(tgt_kmh, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
            ax1.axvline(tgt_s,   color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
        for t_val, v_val in [(T_48, 48.3), (T_96, 96.6)]:
            if t_val is not None:
                ax1.plot(t_val, v_val, "o", color="#E64A19", zorder=5)
                ax1.annotate(f"{t_val:.1f} s", (t_val, v_val),
                             textcoords="offset points", xytext=(6, -12),
                             fontsize=8, color="#E64A19")
        ax1.set_xlabel("Time (s)", fontsize=10)
        ax1.set_ylabel("Speed (km/h)", fontsize=10)
        ax1.set_title("Speed vs Time", fontsize=11, fontweight="bold")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

    # Plot 2 — Acceleration vs Speed
    with col_right:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(df_sim["Speed (km/h)"], df_sim["Acceleration (m/s²)"],
                 color="#388E3C", linewidth=2)
        ax2.axhline(0, color="red", linestyle="--", linewidth=0.8)
        ax2.set_xlabel("Speed (km/h)", fontsize=10)
        ax2.set_ylabel("Acceleration (m/s²)", fontsize=10)
        ax2.set_title("Acceleration vs Speed", fontsize=11, fontweight="bold")
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # Plot 3 — Tractive Force vs Speed
    with col_left:
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.plot(df_sim["Speed (km/h)"], df_sim["F_available (N)"],
                 color="#7B1FA2", linewidth=2, label="F available (best gear)")
        ax3.plot(df_sim["Speed (km/h)"], df_sim["F_resistance (N)"],
                 color="#E64A19", linewidth=2, linestyle="--", label="F resistance")
        ax3.set_xlabel("Speed (km/h)", fontsize=10)
        ax3.set_ylabel("Force (N)", fontsize=10)
        ax3.set_title("Tractive Force vs Speed", fontsize=11, fontweight="bold")
        ax3.legend(fontsize=8)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    # Plot 4 — Selected Gear vs Speed
    with col_right:
        # Convert gear column to numeric for plotting (drop non-numeric rows)
        gear_numeric = pd.to_numeric(df_sim["Gear"], errors="coerce").dropna()
        speed_for_gear = df_sim.loc[gear_numeric.index, "Speed (km/h)"]
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        ax4.step(speed_for_gear, gear_numeric,
                 color="#0288D1", linewidth=2, where="post")
        ax4.set_xlabel("Speed (km/h)", fontsize=10)
        ax4.set_ylabel("Gear", fontsize=10)
        n_gears = len(vp["gear_ratios"])
        ax4.set_yticks(range(1, n_gears + 1))
        ax4.set_title("Selected Gear vs Speed", fontsize=11, fontweight="bold")
        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

    # ── Expandable Simulation Table ───────────────────────────────────────────
    with st.expander("Simulation Data Table", expanded=False):
        st.caption(
            "Step-by-step output. Each row shows conditions at the start of that "
            "speed band. Cumulative time is the elapsed time to reach that speed."
        )
        st.dataframe(df_sim, use_container_width=True, hide_index=True)

else:
    st.info("Increase the simulation speed range (target > start) to run the simulation.")
