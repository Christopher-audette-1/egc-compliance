# EGC Compliance - Implementation Status

## Overview

This is a standalone Python CLI application for ASHRAE 90.1-2022 Energy Code Compliance analysis, adapted from the existing `audette-orchestrator/skills/egc-compliance` skill code.

## What's Been Adapted

### ✅ Complete Modules

1. **models.py** - Pydantic v2 domain models
   - All enums (ClimateZone, OccupancyType, system types)
   - Building data models (Envelope, HVAC, Lighting, Utility)
   - Simulation models (ScenarioResult, EndUseBreakdown)
   - Compliance models (PrescriptiveCheck, ComplianceReport)

2. **config/** - Configuration tables
   - `ashrae_901_2022.py` - Code minimums for all 17 climate zones
   - `appendix_g.py` - Appendix G baseline system determination
   - `weather_files.py` - EPW file mappings and download URLs
   - `energy_rates.py` - Default utility rates for all 50 states + DC

3. **simulation/** - EnergyPlus execution
   - `runner.py` - Parallel simulation execution (from orchestrator)
   - `parser.py` - CSV/ESO output parsing with joules→kWh conversion
   - `weather_manager.py` - EPW file download and caching (from orchestrator)

4. **compliance/** - Code checking
   - `checker.py` - 9 prescriptive checks against ASHRAE 90.1-2022
   - Score calculation (passes/total)

5. **report/** - HTML generation
   - `generator.py` - Jinja2 template rendering
   - `templates/report.html.j2` - Self-contained HTML template (from Taildrop)

6. **cli.py** - Click interface
   - `egc-compliance run <building_uid>` - Main command
   - `egc-compliance list-buildings` - List available buildings
   - `egc-compliance check-install` - Verify EnergyPlus
   - All options: --output-dir, --open, --verbose, etc.

7. **Tests** - pytest test suite
   - `test_compliance.py` - Prescriptive compliance checker tests

### 📦 Adapted from Orchestrator

These modules were copied from `audette-orchestrator/skills/egc-compliance/lib/` and are being used directly:

- `scenario_engine.py` - 4-scenario orchestration
- `model_adapter.py` - Flat schema → IDF payload conversion
- `artifact_builder.py` - HTML artifact generation
- `idf/generator.py` - EnergyPlus IDF file generation
- `calibration/calibrator.py` - Utility calibration logic
- `audette_client.py` - MCP data retrieval (was `building_collector.py`)

### ⚠️ Needs Integration

The following modules exist but need minor adjustments to work with Pydantic models:

1. **scenario_engine.py**
   - Currently uses dicts
   - Needs to accept `BuildingModel` and return `ScenarioResult` objects

2. **audette_client.py**
   - Currently returns dicts
   - Needs to return `BuildingModel` Pydantic object

3. **calibration/calibrator.py**
   - Works with dicts
   - Needs to work with `UtilityData` and `ScenarioResult` models

4. **cli.py**
   - Basic flow implemented
   - Needs actual integration with scenario engine and calibration
   - TODO markers where integration needed

### 🔧 Quick Integration Steps

To make this fully functional:

1. **Update scenario_engine.py**:
   ```python
   def __init__(self, building_model: BuildingModel, climate_zone: str):
       self.building = building_model  # Accept Pydantic model
   ```

2. **Update audette_client.py**:
   ```python
   def fetch_building_data(building_uid: str) -> BuildingModel:
       # MCP calls here
       return BuildingModel(**data)  # Return Pydantic model
   ```

3. **Update calibration/calibrator.py**:
   ```python
   def calibrate_results(
       scenarios: dict[SimulationScenario, ScenarioResult],
       utility: UtilityData
   ) -> dict[SimulationScenario, ScenarioResult]:
       # Apply calibration
   ```

4. **Complete cli.py integration**:
   - Replace TODO markers with actual calls
   - Convert dict results to Pydantic `ScenarioResult` objects
   - Apply calibration before building `ComplianceReport`

## Testing

```bash
# Run tests
pytest

# Check installation
egc-compliance check-install

# Generate report (after integration)
egc-compliance run <building_uid> --open
```

## Dependencies

All dependencies are specified in `pyproject.toml`:
- pydantic>=2.0 (domain models)
- jinja2>=3.1 (report templates)
- click>=8.1 (CLI)
- eppy>=0.5.63 (IDF generation)
- requests>=2.31 (weather file downloads)
- rich>=13.0 (CLI formatting)

## Next Steps

1. Test the Pydantic models with actual building data
2. Integrate scenario_engine with BuildingModel
3. Test full run command end-to-end
4. Add more comprehensive test coverage
5. Add IDF validation logic
6. Enhance error handling and user messaging

## Notes

- This adaptation preserves all the working logic from the orchestrator skill
- The main change is wrapping everything in Pydantic models for type safety
- The CLI provides a standalone executable: `pip install -e .` then `egc-compliance`
- Report templates are self-contained (all CSS/JS inline for offline use)
