"""Report generator - renders Jinja2 template to HTML."""

from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from egc_compliance.models import BuildingModel, ComplianceReport


def generate_html_report(
    building: BuildingModel,
    report: ComplianceReport,
    output_path: str | Path
) -> None:
    """
    Generate self-contained HTML compliance report.

    Args:
        building: Complete building model
        report: Compliance analysis results
        output_path: Where to write the HTML file
    """
    # Set up Jinja2 environment
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Load template
    template = env.get_template("report.html.j2")

    # Extract scenario results for easy access in template
    as_built = report.scenarios.get("as_built")
    doe_ref = report.scenarios.get("doe_ref")
    code_min = report.scenarios.get("code_min")
    retrofit = report.scenarios.get("retrofit")

    # Calculate compliance score
    passes = sum(1 for check in report.prescriptive_checks if check.passes)
    total = len(report.prescriptive_checks)
    compliance_score = f"{passes}/{total}"

    # Calculate savings metrics
    if as_built and retrofit:
        retrofit_savings_usd = as_built.annual_energy_cost_usd - retrofit.annual_energy_cost_usd
        retrofit_eui_reduction_pct = (as_built.eui_kwh_per_sqft - retrofit.eui_kwh_per_sqft) / as_built.eui_kwh_per_sqft
    else:
        retrofit_savings_usd = 0
        retrofit_eui_reduction_pct = 0

    # Prepare template context
    context = {
        "building": building,
        "report": report,
        "as_built": as_built,
        "doe_ref": doe_ref,
        "code_min": code_min,
        "retrofit": retrofit,
        "prescriptive_checks": report.prescriptive_checks,
        "compliance_score": compliance_score,
        "baseline_period": report.baseline_period_label,
        "generated_at": datetime.now().strftime("%B %d, %Y"),
        "retrofit_savings_usd": retrofit_savings_usd,
        "retrofit_eui_reduction_pct": retrofit_eui_reduction_pct,
    }

    # Render template
    html_content = template.render(**context)

    # Write to file
    output_path = Path(output_path)
    output_path.write_text(html_content, encoding='utf-8')


def generate_print_preview(
    building: BuildingModel,
    report: ComplianceReport,
    output_path: str | Path
) -> None:
    """
    Generate print-optimized version of the report.

    Same data as interactive report but with all tabs expanded
    and print-friendly CSS.

    Args:
        building: Complete building model
        report: Compliance analysis results
        output_path: Where to write the HTML file
    """
    # For now, use the same generator
    # TODO: Create a separate print-optimized template
    generate_html_report(building, report, output_path)
