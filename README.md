# EGC Compliance

ASHRAE 90.1-2022 Energy Code Compliance report generator.

## Overview

`egc-compliance` is a Python CLI application that generates ASHRAE 90.1-2022 Energy Code Compliance reports. The application:

- Pulls building data from the Audette MCP
- Runs four EnergyPlus simulation scenarios (As-Built, DoE Reference, Code Minimum, Retrofit)
- Calibrates outputs to actual utility data with weather normalization
- Checks prescriptive code compliance
- Renders a self-contained interactive HTML report

## Installation

```bash
pip install -e .
```

## Requirements

- Python 3.11+
- EnergyPlus 24.1.0 (download from https://energyplus.net/downloads)

## Usage

```bash
# Generate report for a building in Audette
egc-compliance run <building_uid>

# List available buildings
egc-compliance list-buildings

# Check EnergyPlus installation
egc-compliance check-install

# Generate report from JSON config file
egc-compliance run --config building.json

# Open report in browser after generation
egc-compliance run <building_uid> --open
```

## Options

- `--output-dir PATH` - Directory to write HTML files [default: ./]
- `--open` - Open the report in the default browser after generation
- `--no-parallel` - Run simulations sequentially (useful for debugging)
- `--keep-idf` - Do not delete IDF and simulation working files after run
- `--energy-plus PATH` - Path to EnergyPlus binary [overrides auto-detection]
- `--elec-rate FLOAT` - Electricity rate USD/kWh [overrides Audette + state default]
- `--gas-rate FLOAT` - Gas rate USD/kWh [overrides Audette + state default]
- `--verbose / -v` - Verbose logging

## Output

Two HTML files are generated per run:

1. `{building_name} EGC Compliance.html` - Interactive tabbed report (screen-optimized)
2. `{building_name} EGC Compliance — Print Preview.html` - Print-optimized layout

Both files are fully self-contained (all JS/CSS inline) and can be opened offline.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=egc_compliance

# Format code
ruff format .

# Type check
mypy egc_compliance
```
