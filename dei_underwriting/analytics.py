"""Portfolio analytics for the DEI Risk Engine."""

from collections import Counter, defaultdict
from statistics import mean, median

from .models import ScoredCompany


FACTOR_LABELS = {
    "industry_exposure": "Industry exposure",
    "data_sensitivity": "Data sensitivity",
    "cloud_dependency": "Cloud dependency",
    "vendor_exposure": "Vendor exposure",
    "workforce_distribution": "Workforce distribution",
    "prior_incidents": "Prior incidents",
    "regulatory_exposure": "Regulatory exposure",
}


def analyze_portfolio(results: list[ScoredCompany]) -> dict[str, object]:
    """Build portfolio-level analytics from scored underwriting results."""

    if not results:
        raise ValueError("results cannot be empty")

    scores = [result.dei_score for result in results]
    severe_count = sum(1 for result in results if result.risk_tier == "Severe")

    return {
        "account_count": len(results),
        "average_dei_score": round(mean(scores), 1),
        "median_dei_score": round(median(scores), 1),
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "severe_risk_count": severe_count,
        "severe_risk_percentage": round(severe_count / len(results) * 100, 1),
        "highest_risk_industries": highest_risk_industries(results),
        "decision_distribution": distribution_by(results, "underwriting_decision"),
        "risk_tier_distribution": distribution_by(results, "risk_tier"),
        "risk_segmentation": risk_segmentation(results),
        "top_contributing_risk_factors": top_contributing_risk_factors(results),
        "industry_factor_heatmap": industry_factor_heatmap(results),
    }


def highest_risk_industries(results: list[ScoredCompany]) -> list[dict[str, object]]:
    """Rank industries by average DEI score."""

    grouped = defaultdict(list)

    for result in results:
        grouped[result.profile.industry].append(result)

    rows = []
    for industry, industry_results in grouped.items():
        scores = [result.dei_score for result in industry_results]
        rows.append(
            {
                "industry": industry,
                "account_count": len(industry_results),
                "average_dei_score": round(mean(scores), 1),
                "severe_count": sum(1 for result in industry_results if result.risk_tier == "Severe"),
                "elevated_or_severe_count": sum(
                    1 for result in industry_results if result.risk_tier in {"Elevated", "Severe"}
                ),
            }
        )

    return sorted(rows, key=lambda row: row["average_dei_score"], reverse=True)


def distribution_by(results: list[ScoredCompany], attribute: str) -> dict[str, int]:
    """Return counts for a ScoredCompany attribute."""

    return dict(Counter(getattr(result, attribute) for result in results))


def risk_segmentation(results: list[ScoredCompany]) -> list[dict[str, object]]:
    """Return industry-by-tier segmentation for portfolio reporting."""

    grouped = defaultdict(lambda: Counter())

    for result in results:
        grouped[result.profile.industry][result.risk_tier] += 1

    rows = []
    for industry, tiers in grouped.items():
        row = {"industry": industry}
        for tier in ["Low", "Moderate", "Elevated", "Severe"]:
            row[tier] = tiers.get(tier, 0)
        rows.append(row)

    return sorted(rows, key=lambda row: row["industry"])


def top_contributing_risk_factors(results: list[ScoredCompany]) -> list[dict[str, object]]:
    """Rank risk factors by average contribution across the portfolio."""

    totals = defaultdict(float)

    for result in results:
        for factor, value in result.breakdown.positive_components().items():
            totals[factor] += value

    rows = [
        {
            "risk_factor": FACTOR_LABELS[factor],
            "average_contribution": round(total / len(results), 1),
            "total_contribution": round(total, 1),
        }
        for factor, total in totals.items()
    ]

    return sorted(rows, key=lambda row: row["average_contribution"], reverse=True)


def industry_factor_heatmap(results: list[ScoredCompany]) -> list[dict[str, object]]:
    """Average risk factor contribution by industry."""

    grouped = defaultdict(list)

    for result in results:
        grouped[result.profile.industry].append(result)

    rows = []
    for industry, industry_results in grouped.items():
        row: dict[str, object] = {"industry": industry}
        for factor, label in FACTOR_LABELS.items():
            row[label] = round(
                mean(result.breakdown.positive_components()[factor] for result in industry_results),
                1,
            )
        row["Average DEI"] = round(mean(result.dei_score for result in industry_results), 1)
        rows.append(row)

    return sorted(rows, key=lambda row: row["Average DEI"], reverse=True)
