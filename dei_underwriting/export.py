"""Export helpers for analytics-ready DEI outputs."""

from csv import DictWriter
from pathlib import Path

from .models import ScenarioResult, ScoredCompany, SensitivityResult


RESULT_FIELDS = [
    "company_name",
    "industry",
    "annual_revenue",
    "employee_count",
    "data_sensitivity",
    "cloud_dependency",
    "remote_workforce_percentage",
    "third_party_vendor_exposure",
    "security_maturity",
    "historical_incident_count",
    "regulatory_exposure",
    "dei_score",
    "risk_tier",
    "underwriting_decision",
    "premium_range",
    "estimated_risk_profile_summary",
    "key_risk_drivers",
    "recommended_mitigation_actions",
    "explanation",
    "industry_exposure_points",
    "data_sensitivity_points",
    "cloud_dependency_points",
    "vendor_exposure_points",
    "workforce_distribution_points",
    "prior_incidents_points",
    "regulatory_exposure_points",
    "security_maturity_credit",
]


def result_to_row(result: ScoredCompany) -> dict[str, str | int | float]:
    """Flatten a scored company into a Power BI-friendly CSV row."""

    profile = result.profile
    breakdown = result.breakdown

    return {
        "company_name": profile.company_name,
        "industry": profile.industry,
        "annual_revenue": profile.annual_revenue,
        "employee_count": profile.employee_count,
        "data_sensitivity": profile.data_sensitivity,
        "cloud_dependency": profile.cloud_dependency,
        "remote_workforce_percentage": profile.remote_workforce_percentage,
        "third_party_vendor_exposure": profile.third_party_vendor_exposure,
        "security_maturity": profile.security_maturity,
        "historical_incident_count": profile.historical_incident_count,
        "regulatory_exposure": profile.regulatory_exposure,
        "dei_score": result.dei_score,
        "risk_tier": result.risk_tier,
        "underwriting_decision": result.underwriting_decision,
        "premium_range": result.premium_range,
        "estimated_risk_profile_summary": result.estimated_risk_profile_summary,
        "key_risk_drivers": "; ".join(result.key_risk_drivers),
        "recommended_mitigation_actions": "; ".join(result.recommended_mitigation_actions),
        "explanation": result.explanation,
        "industry_exposure_points": round(breakdown.industry_exposure, 1),
        "data_sensitivity_points": round(breakdown.data_sensitivity, 1),
        "cloud_dependency_points": round(breakdown.cloud_dependency, 1),
        "vendor_exposure_points": round(breakdown.vendor_exposure, 1),
        "workforce_distribution_points": round(breakdown.workforce_distribution, 1),
        "prior_incidents_points": round(breakdown.prior_incidents, 1),
        "regulatory_exposure_points": round(breakdown.regulatory_exposure, 1),
        "security_maturity_credit": round(breakdown.security_maturity_credit, 1),
    }


def export_results(results: list[ScoredCompany], output_path: str | Path) -> Path:
    """Export account-level underwriting results to CSV."""

    return _write_csv(output_path, RESULT_FIELDS, [result_to_row(result) for result in results])


def export_portfolio_summary(summary: dict[str, object], output_dir: str | Path) -> list[Path]:
    """Export portfolio analytics summary tables to CSV."""

    output = Path(output_dir)
    paths = [
        _write_csv(
            output / "portfolio_summary.csv",
            ["metric", "value"],
            [
                {"metric": "account_count", "value": summary["account_count"]},
                {"metric": "average_dei_score", "value": summary["average_dei_score"]},
                {"metric": "median_dei_score", "value": summary["median_dei_score"]},
                {"metric": "highest_score", "value": summary["highest_score"]},
                {"metric": "lowest_score", "value": summary["lowest_score"]},
                {"metric": "severe_risk_count", "value": summary["severe_risk_count"]},
                {"metric": "severe_risk_percentage", "value": summary["severe_risk_percentage"]},
            ],
        ),
        _write_csv(
            output / "industry_risk_summary.csv",
            ["industry", "account_count", "average_dei_score", "severe_count", "elevated_or_severe_count"],
            summary["highest_risk_industries"],
        ),
        _write_csv(
            output / "risk_tier_distribution.csv",
            ["risk_tier", "account_count"],
            _distribution_rows(summary["risk_tier_distribution"], "risk_tier"),
        ),
        _write_csv(
            output / "underwriting_decision_distribution.csv",
            ["underwriting_decision", "account_count"],
            _distribution_rows(summary["decision_distribution"], "underwriting_decision"),
        ),
        _write_csv(
            output / "risk_segmentation_breakdown.csv",
            ["industry", "Low", "Moderate", "Elevated", "Severe"],
            summary["risk_segmentation"],
        ),
        _write_csv(
            output / "top_risk_factor_contributions.csv",
            ["risk_factor", "average_contribution", "total_contribution"],
            summary["top_contributing_risk_factors"],
        ),
        _write_csv(
            output / "industry_factor_heatmap.csv",
            list(summary["industry_factor_heatmap"][0].keys()),
            summary["industry_factor_heatmap"],
        ),
    ]

    return paths


def export_scenario_results(results: list[ScenarioResult], output_path: str | Path) -> Path:
    """Export scenario simulation results to CSV."""

    fields = [
        "company_name",
        "scenario_name",
        "baseline_score",
        "scenario_score",
        "score_change",
        "baseline_tier",
        "scenario_tier",
        "baseline_decision",
        "scenario_decision",
    ]
    return _write_csv(output_path, fields, [result.__dict__ for result in results])


def export_sensitivity_results(results: list[SensitivityResult], output_path: str | Path) -> Path:
    """Export sensitivity analysis results to CSV."""

    fields = [
        "company_name",
        "factor",
        "baseline_score",
        "adjusted_score",
        "score_change",
        "note",
    ]
    return _write_csv(output_path, fields, [result.__dict__ for result in results])


def _distribution_rows(distribution: dict[str, int], key_name: str) -> list[dict[str, object]]:
    return [{key_name: key, "account_count": value} for key, value in distribution.items()]


def _write_csv(
    output_path: str | Path,
    fieldnames: list[str],
    rows: list[dict[str, object]],
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return path
