"""Prescriptive compliance checker against ASHRAE 90.1-2022."""

from egc_compliance.models import BuildingModel, PrescriptiveCheck
from egc_compliance.config.ashrae_901_2022 import ASHRAE_901_2022_MINIMUMS


def check_prescriptive_compliance(building: BuildingModel) -> list[PrescriptiveCheck]:
    """
    Generate prescriptive compliance checks against ASHRAE 90.1-2022.

    Args:
        building: Complete building model

    Returns:
        List of 9 prescriptive checks (wall, roof, slab, window U/SHGC,
        heating/cooling/DHW efficiency, LPD)
    """
    # Get code minimums for this climate zone
    code_mins = ASHRAE_901_2022_MINIMUMS[building.climate_zone]

    checks = []

    # 1. Wall insulation (CI path vs. cavity path)
    wall_ci_ok = building.envelope.wall_r_value_ci >= code_mins.wall_r_ci_min
    wall_cavity_ok = building.envelope.wall_r_value_cavity >= code_mins.wall_r_cavity_min
    wall_passes = wall_ci_ok and wall_cavity_ok

    if building.envelope.wall_r_value_ci == 0:
        actual_wall = f"R-{building.envelope.wall_r_value_cavity:.1f} cavity only (no CI)"
    else:
        actual_wall = f"R-{building.envelope.wall_r_value_cavity:.1f} + CI R-{building.envelope.wall_r_value_ci:.1f}"

    checks.append(PrescriptiveCheck(
        name="Wall insulation",
        requirement=f"R-{code_mins.wall_r_cavity_min:.1f} + CI R-{code_mins.wall_r_ci_min:.1f}",
        actual_value=actual_wall,
        passes=wall_passes
    ))

    # 2. Roof insulation
    roof_passes = building.envelope.roof_r_value >= code_mins.roof_r_min
    checks.append(PrescriptiveCheck(
        name="Roof insulation",
        requirement=f"R-{code_mins.roof_r_min:.1f} min",
        actual_value=f"R-{building.envelope.roof_r_value:.1f}",
        passes=roof_passes
    ))

    # 3. Slab insulation
    slab_r_ok = building.envelope.slab_r_value >= code_mins.slab_r_min
    slab_depth_ok = building.envelope.slab_depth_ft >= code_mins.slab_depth_ft_min
    slab_passes = slab_r_ok and slab_depth_ok

    if building.envelope.slab_r_value == 0:
        actual_slab = "No slab insulation"
    else:
        actual_slab = f"R-{building.envelope.slab_r_value:.1f} @ {building.envelope.slab_depth_ft:.1f} ft depth"

    req_slab = f"R-{code_mins.slab_r_min:.1f} @ {code_mins.slab_depth_ft_min:.1f} ft depth" if code_mins.slab_r_min > 0 else "None required"

    checks.append(PrescriptiveCheck(
        name="Slab insulation",
        requirement=req_slab,
        actual_value=actual_slab,
        passes=slab_passes
    ))

    # 4. Window U-factor
    window_u_passes = building.envelope.window_u_factor <= code_mins.window_u_max
    checks.append(PrescriptiveCheck(
        name="Window U-factor",
        requirement=f"U-{code_mins.window_u_max:.2f} max",
        actual_value=f"U-{building.envelope.window_u_factor:.2f}",
        passes=window_u_passes
    ))

    # 5. Window SHGC
    window_shgc_passes = building.envelope.window_shgc <= code_mins.window_shgc_max
    checks.append(PrescriptiveCheck(
        name="Window SHGC",
        requirement=f"{code_mins.window_shgc_max:.2f} max",
        actual_value=f"{building.envelope.window_shgc:.2f}",
        passes=window_shgc_passes
    ))

    # 6. Heating efficiency (AFUE for gas, COP for heat pump)
    heating_passes = building.hvac.heating_efficiency >= code_mins.heating_eff_min

    # Format depends on system type
    if "gas" in building.hvac.heating_type.value.lower():
        heating_unit = "AFUE"
        actual_heating = f"{building.hvac.heating_efficiency:.1%} {heating_unit}"
        req_heating = f"{code_mins.heating_eff_min:.1%} {heating_unit} min"
    else:
        heating_unit = "COP"
        actual_heating = f"{building.hvac.heating_efficiency:.2f} {heating_unit}"
        req_heating = f"{code_mins.heating_eff_min:.2f} {heating_unit} min"

    checks.append(PrescriptiveCheck(
        name="Heating efficiency",
        requirement=req_heating,
        actual_value=actual_heating,
        passes=heating_passes
    ))

    # 7. Cooling efficiency (EER)
    cooling_passes = building.hvac.cooling_efficiency >= code_mins.cooling_eer_min
    checks.append(PrescriptiveCheck(
        name="Cooling efficiency",
        requirement=f"{code_mins.cooling_eer_min:.1f} EER min",
        actual_value=f"{building.hvac.cooling_efficiency:.1f} EER",
        passes=cooling_passes
    ))

    # 8. DHW efficiency (EF)
    dhw_passes = building.hvac.dhw_efficiency >= code_mins.dhw_ef_min

    # HPWH uses COP, gas uses EF
    if "heat_pump" in building.hvac.dhw_type.value.lower():
        dhw_unit = "COP"
        actual_dhw = f"{building.hvac.dhw_efficiency:.2f} {dhw_unit}"
        req_dhw = f"{code_mins.dhw_ef_min:.2f} EF min (or equiv. COP)"
    else:
        dhw_unit = "EF"
        actual_dhw = f"{building.hvac.dhw_efficiency:.2f} {dhw_unit}"
        req_dhw = f"{code_mins.dhw_ef_min:.2f} {dhw_unit} min"

    checks.append(PrescriptiveCheck(
        name="DHW efficiency",
        requirement=req_dhw,
        actual_value=actual_dhw,
        passes=dhw_passes
    ))

    # 9. Lighting power density
    lpd_passes = building.lighting.lpd_w_per_sqft <= code_mins.lpd_max_w_per_sqft
    checks.append(PrescriptiveCheck(
        name="Lighting power density",
        requirement=f"{code_mins.lpd_max_w_per_sqft:.2f} W/ft² max",
        actual_value=f"{building.lighting.lpd_w_per_sqft:.2f} W/ft²",
        passes=lpd_passes
    ))

    return checks


def compute_compliance_score(checks: list[PrescriptiveCheck]) -> tuple[int, int]:
    """
    Compute compliance score as (passes, total).

    Args:
        checks: List of prescriptive checks

    Returns:
        Tuple of (number_passing, total_checks)
    """
    passes = sum(1 for check in checks if check.passes)
    total = len(checks)
    return (passes, total)
