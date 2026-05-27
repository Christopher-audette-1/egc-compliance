"""Tests for compliance checker."""

import pytest
from egc_compliance.models import (
    BuildingModel, ClimateZone, OccupancyType, EnvelopeData,
    HVACData, LightingData, UtilityData, UtilityMonth,
    HeatingSystemType, CoolingSystemType, DHWSystemType
)
from egc_compliance.compliance.checker import check_prescriptive_compliance, compute_compliance_score


def test_compliant_building_5a():
    """Test a building that passes all prescriptive checks in CZ 5A."""
    building = BuildingModel(
        building_uid="test-001",
        name="Compliant Building",
        address="123 Main St",
        city="Boston",
        state="MA",
        zip_code="02101",
        climate_zone=ClimateZone.CZ_5A,
        occupancy_type=OccupancyType.MULTIFAMILY_RESIDENTIAL,
        gfa_sqft=50000,
        stories=4,
        year_built=2022,
        envelope=EnvelopeData(
            wall_r_value_ci=8.0,  # > 7.5 min
            wall_r_value_cavity=13.0,  # = 13 min
            roof_r_value=30.0,  # = 30 min
            slab_r_value=10.0,  # = 10 min
            slab_depth_ft=2.0,  # = 2.0 min
            window_u_factor=0.40,  # < 0.42 max
            window_shgc=0.38,  # < 0.40 max
            window_to_wall_ratio=0.30
        ),
        hvac=HVACData(
            heating_type=HeatingSystemType.ASHP,
            heating_efficiency=3.3,  # COP = 3.3, > 0.80 min
            cooling_type=CoolingSystemType.SPLIT_DX,
            cooling_efficiency=12.0,  # > 12.0 min
            dhw_type=DHWSystemType.HEAT_PUMP_WH,
            dhw_efficiency=2.5  # COP > 0.80 min
        ),
        lighting=LightingData(
            lpd_w_per_sqft=0.55,  # < 0.60 max
            fraction_led=1.0
        ),
        plug_load_density_w_per_sqft=0.5,
        utility=UtilityData(
            months=[
                UtilityMonth(year=2025, month=i, electricity_kwh=10000, gas_kwh=5000)
                for i in range(1, 13)
            ],
            weather_normalized_eui_kwh_per_sqft=45.0,
            electricity_rate_usd_per_kwh=0.27,
            gas_rate_usd_per_kwh=0.058
        ),
        retrofit_ecms=[]
    )

    checks = check_prescriptive_compliance(building)
    passes, total = compute_compliance_score(checks)

    assert passes == 9
    assert total == 9
    assert all(check.passes for check in checks)


def test_noncompliant_window_u():
    """Test a building that fails window U-factor check."""
    building = BuildingModel(
        building_uid="test-002",
        name="Poor Windows",
        address="456 Oak Ave",
        city="Boston",
        state="MA",
        zip_code="02101",
        climate_zone=ClimateZone.CZ_5A,
        occupancy_type=OccupancyType.MULTIFAMILY_RESIDENTIAL,
        gfa_sqft=50000,
        stories=4,
        year_built=1985,
        envelope=EnvelopeData(
            wall_r_value_ci=8.0,
            wall_r_value_cavity=13.0,
            roof_r_value=30.0,
            slab_r_value=10.0,
            slab_depth_ft=2.0,
            window_u_factor=0.50,  # FAILS: > 0.42 max for CZ 5A
            window_shgc=0.38,
            window_to_wall_ratio=0.30
        ),
        hvac=HVACData(
            heating_type=HeatingSystemType.GAS_BOILER,
            heating_efficiency=0.82,
            cooling_type=CoolingSystemType.PTAC,
            cooling_efficiency=12.0,
            dhw_type=DHWSystemType.GAS_STORAGE,
            dhw_efficiency=0.82
        ),
        lighting=LightingData(
            lpd_w_per_sqft=0.55,
            fraction_led=0.8
        ),
        plug_load_density_w_per_sqft=0.5,
        utility=UtilityData(
            months=[
                UtilityMonth(year=2025, month=i, electricity_kwh=10000, gas_kwh=8000)
                for i in range(1, 13)
            ],
            weather_normalized_eui_kwh_per_sqft=55.0,
            electricity_rate_usd_per_kwh=0.27,
            gas_rate_usd_per_kwh=0.058
        ),
        retrofit_ecms=[]
    )

    checks = check_prescriptive_compliance(building)
    passes, total = compute_compliance_score(checks)

    assert passes == 8
    assert total == 9

    # Find the failed check
    window_u_check = next(c for c in checks if c.name == "Window U-factor")
    assert not window_u_check.passes
    assert "U-0.50" in window_u_check.actual_value
    assert "U-0.42" in window_u_check.requirement
