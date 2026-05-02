"""Console and executive reporting helpers."""

from pathlib import Path
from textwrap import fill

from .models import ScoredCompany


TABLE_COLUMNS = [
    ("company_name", "Company"),
    ("industry", "Industry"),
    ("annual_revenue", "Revenue"),
    ("employee_count", "Employees"),
    ("data_sensitivity", "Data"),
    ("cloud_dependency", "Cloud"),
    ("remote_workforce_percentage", "Remote"),
    ("third_party_vendor_exposure", "Vendor"),
    ("security_maturity", "Security"),
    ("historical_incident_count", "Inc"),
    ("regulatory_exposure", "Reg"),
    ("dei_score", "DEI"),
    ("risk_tier", "Tier"),
    ("underwriting_decision", "Decision"),
    ("premium_range", "Premium Range"),
]


def build_results_table(results: list[ScoredCompany]) -> str:
    """Return a fixed-width underwriting results table."""

    rows = [_result_to_display_row(result) for result in results]
    widths = _column_widths(rows)

    header = " | ".join(label.ljust(widths[key]) for key, label in TABLE_COLUMNS)
    divider = "-+-".join("-" * widths[key] for key, _ in TABLE_COLUMNS)
    body = [
        " | ".join(str(row[key]).ljust(widths[key]) for key, _ in TABLE_COLUMNS)
        for row in rows
    ]

    return "\n".join([header, divider, *body])


def build_explanations(results: list[ScoredCompany], width: int = 110) -> str:
    """Return wrapped account-level underwriting explanations."""

    sections = []

    for result in results:
        actions = " ".join(result.recommended_mitigation_actions)
        sections.append(f"{result.profile.company_name}:")
        sections.append(fill(result.explanation, width=width, subsequent_indent="  "))
        sections.append(fill(f"Mitigation actions: {actions}", width=width, subsequent_indent="  "))

    return "\n\n".join(sections)


def build_portfolio_summary(summary: dict[str, object]) -> str:
    """Return an executive-style portfolio analytics summary."""

    severe_percentage = summary["severe_risk_percentage"]
    highest_industries = summary["highest_risk_industries"][:3]
    top_factors = summary["top_contributing_risk_factors"][:3]

    lines = [
        "Portfolio Analytics Summary",
        f"Accounts analyzed: {summary['account_count']}",
        f"Average DEI score: {summary['average_dei_score']}",
        f"Median DEI score: {summary['median_dei_score']}",
        f"Severe-risk concentration: {summary['severe_risk_count']} accounts ({severe_percentage}%)",
        "",
        "Highest-risk industries:",
    ]

    for row in highest_industries:
        lines.append(
            f"- {row['industry']}: average DEI {row['average_dei_score']} across {row['account_count']} account(s)"
        )

    lines.append("")
    lines.append("Top contributing risk factors:")
    for row in top_factors:
        lines.append(f"- {row['risk_factor']}: average contribution {row['average_contribution']}")

    lines.append("")
    lines.append("Underwriting decision distribution:")
    for decision, count in summary["decision_distribution"].items():
        lines.append(f"- {decision}: {count}")

    return "\n".join(lines)


def write_executive_report(
    results: list[ScoredCompany],
    summary: dict[str, object],
    output_path: str | Path,
) -> Path:
    """Write a text executive report for internal underwriting review."""

    report = "\n\n".join(
        [
            "Digital Exposure Index (DEI) Risk Engine Executive Report",
            build_portfolio_summary(summary),
            "Highest-Risk Accounts",
            _highest_risk_accounts(results),
            "Account-Level Explainability",
            build_explanations(results),
        ]
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return path


def _highest_risk_accounts(results: list[ScoredCompany]) -> str:
    rows = sorted(results, key=lambda result: result.dei_score, reverse=True)[:5]
    return "\n".join(
        f"- {result.profile.company_name}: DEI {result.dei_score:.1f}, {result.risk_tier}, "
        f"{result.underwriting_decision}"
        for result in rows
    )


def _result_to_display_row(result: ScoredCompany) -> dict[str, str]:
    profile = result.profile

    return {
        "company_name": profile.company_name,
        "industry": profile.industry,
        "annual_revenue": _money(profile.annual_revenue),
        "employee_count": f"{profile.employee_count:,}",
        "data_sensitivity": profile.data_sensitivity,
        "cloud_dependency": profile.cloud_dependency,
        "remote_workforce_percentage": f"{profile.remote_workforce_percentage}%",
        "third_party_vendor_exposure": profile.third_party_vendor_exposure,
        "security_maturity": profile.security_maturity,
        "historical_incident_count": str(profile.historical_incident_count),
        "regulatory_exposure": profile.regulatory_exposure,
        "dei_score": f"{result.dei_score:.1f}",
        "risk_tier": result.risk_tier,
        "underwriting_decision": result.underwriting_decision,
        "premium_range": result.premium_range,
    }


def _money(value: int) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    return f"${value / 1_000_000:.0f}M"


def _column_widths(rows: list[dict[str, str]]) -> dict[str, int]:
    widths = {}

    for key, label in TABLE_COLUMNS:
        widths[key] = max(len(label), *(len(row[key]) for row in rows))

    return widths
