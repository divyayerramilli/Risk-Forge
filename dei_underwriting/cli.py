"""Command line entry point for the DEI Risk Engine."""

import argparse
from pathlib import Path

from .analytics import analyze_portfolio
from .data import SAMPLE_COMPANIES
from .export import (
    export_portfolio_summary,
    export_results,
    export_scenario_results,
    export_sensitivity_results,
)
from .reporting import (
    build_portfolio_summary,
    build_results_table,
    write_executive_report,
)
from .scenario import (
    run_sensitivity_analysis,
    simulate_remote_workforce_decrease,
    simulate_security_maturity_improvement,
)
from .scoring import score_companies
from .visualization import generate_industry_heatmap, generate_risk_distribution_chart


DEFAULT_OUTPUT_DIR = "outputs"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Digital Exposure Index Risk Engine underwriting analytics platform."
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for CSV, SVG, and report files. Defaults to {DEFAULT_OUTPUT_DIR}.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    results = score_companies(SAMPLE_COMPANIES)
    summary = analyze_portfolio(results)
    security_scenario = simulate_security_maturity_improvement(SAMPLE_COMPANIES)
    remote_scenario = simulate_remote_workforce_decrease(SAMPLE_COMPANIES)
    sensitivity_results = run_sensitivity_analysis(SAMPLE_COMPANIES)

    output_dir.mkdir(parents=True, exist_ok=True)
    generated_paths = [
        export_results(results, output_dir / "digital_exposure_index_results.csv"),
        *export_portfolio_summary(summary, output_dir),
        export_scenario_results(security_scenario, output_dir / "security_maturity_scenario.csv"),
        export_scenario_results(remote_scenario, output_dir / "remote_workforce_scenario.csv"),
        export_sensitivity_results(sensitivity_results, output_dir / "sensitivity_analysis.csv"),
        generate_risk_distribution_chart(summary, output_dir / "risk_tier_distribution.svg"),
        generate_industry_heatmap(summary, output_dir / "industry_factor_heatmap.svg"),
        write_executive_report(results, summary, output_dir / "executive_report.txt"),
    ]

    print("\nDigital Exposure Index Risk Engine\n")
    print(build_results_table(results))
    print("\n")
    print(build_portfolio_summary(summary))
    print("\nGenerated analytics outputs:")
    for path in generated_paths:
        print(f"- {path}")
