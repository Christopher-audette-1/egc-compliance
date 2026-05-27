"""
Four-phase calibration pipeline for EGC compliance analysis.
Converts raw EnergyPlus IdealLoads output to calibrated site energy.

Phase 1 — Heating efficiency: IdealLoads reports thermal demand (COP=1.0).
           Scale by 1/system_eff to get actual fuel input.
Phase 2 — Cooling efficiency: IdealLoads reports thermal removal.
           Divide by COP (= EER / 3.412141) to get actual electricity.
Phase 3 — DHW injection: Add pre-computed DHW fuel kWh per scenario.
           DHW is occupancy-driven; fuel type switches with system.
Phase 4 — Residual calibration: Fans, pumps, common-area loads not modeled
           by IdealLoads. Compute as platform_baseline - ep_corrected.
           Apply ADDITIVELY to all scenarios (same absolute kWh, not ratio).
"""

BTU_PER_WH = 3.412141

def apply_heating_correction(raw_end_uses, scenario, scenario_heating_factors):
    heat_raw = raw_end_uses.get("heating", 0)
    if heat_raw <= 0:
        return raw_end_uses, 0.0
    factor = scenario_heating_factors.get(scenario, 1.0)
    heat_corr = heat_raw * factor
    raw_end_uses["heating"] = heat_corr
    return raw_end_uses, heat_corr - heat_raw

def apply_cooling_correction(raw_end_uses, scenario, scenario_cooling_cops):
    cool_thermal = raw_end_uses.get("cooling", 0)
    if cool_thermal <= 0:
        return raw_end_uses, 0.0
    cop = scenario_cooling_cops.get(scenario, 1.0)
    cool_elec = cool_thermal / cop
    raw_end_uses["cooling"] = cool_elec
    return raw_end_uses, cool_elec - cool_thermal

def apply_dhw(raw_end_uses, scenario, scenario_dhw):
    dhw = scenario_dhw.get(scenario, {})
    dhw_total = dhw.get("gas", 0.0) + dhw.get("elec", 0.0)
    raw_end_uses.setdefault("dhw_gas", 0.0)
    raw_end_uses.setdefault("dhw_elec", 0.0)
    raw_end_uses["dhw_gas"]  += dhw.get("gas", 0.0)
    raw_end_uses["dhw_elec"] += dhw.get("elec", 0.0)
    return raw_end_uses, dhw_total

def apply_residual(results, platform_baseline_kwh):
    baseline_raw = results.get("baseline", {}).get("raw", {})
    ep_baseline  = baseline_raw.get("total_site_energy_kwh", 0)
    residual     = platform_baseline_kwh - ep_baseline
    for scenario, result in results.items():
        if result.get("success") and result.get("raw"):
            result["raw"]["total_site_energy_kwh"] += residual
    return results, residual

def recalculate_eui(raw, gfa_ft2):
    kwh = raw.get("total_site_energy_kwh", 0)
    raw["eui_kwh_per_sf"]   = kwh / gfa_ft2
    raw["eui_kbtu_per_sf"]  = kwh * BTU_PER_WH / gfa_ft2
    raw["total_site_energy_kbtu"] = kwh * BTU_PER_WH
    return raw

def calibrate_results(results, gfa_ft2, platform_baseline_kwh,
                      scenario_heating_factors, scenario_cooling_cops, scenario_dhw):
    """
    Apply all four calibration phases in order.
    Mutates results in place and returns (results, calibration_report).
    """
    report = {}
    for scenario, result in results.items():
        if not (result.get("success") and result.get("raw")):
            continue
        raw = result["raw"]
        eu  = raw.setdefault("end_uses_kwh", {})

        _, heat_delta = apply_heating_correction(eu, scenario, scenario_heating_factors)
        raw["total_site_energy_kwh"] += heat_delta

        _, cool_delta = apply_cooling_correction(eu, scenario, scenario_cooling_cops)
        raw["total_site_energy_kwh"] += cool_delta

        _, dhw_delta  = apply_dhw(eu, scenario, scenario_dhw)
        raw["total_site_energy_kwh"] += dhw_delta

        report[scenario] = {"heat_delta": heat_delta, "cool_delta": cool_delta, "dhw_delta": dhw_delta}

    results, residual = apply_residual(results, platform_baseline_kwh)
    report["_residual_kwh"] = residual

    for scenario, result in results.items():
        if result.get("success") and result.get("raw"):
            recalculate_eui(result["raw"], gfa_ft2)

    return results, report
