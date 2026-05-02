"""Weighted Digital Exposure Index scoring engine."""

from .models import CompanyProfile, ScoredCompany, ScoreBreakdown
from .underwriting import (
    classify_risk_tier,
    explain_scoring_logic,
    identify_key_risk_drivers,
    premium_range_for_tier,
    recommend_mitigation_actions,
    summarize_risk_profile,
    underwriting_decision_for_tier,
)


LEVEL_FACTORS = {
    "low": 0.25,
    "medium": 0.60,
    "high": 1.00,
}

INDUSTRY_RISK_FACTORS = {
    "finance": 1.00,
    "healthcare": 0.95,
    "legal": 0.88,
    "technology": 0.78,
    "education": 0.76,
    "retail": 0.74,
    "manufacturing": 0.68,
    "logistics": 0.64,
    "nonprofit": 0.55,
}

# The weights total more than 100 before control credit because severe accounts
# can have stacked exposure. Final scores are clipped to a 0-100 DEI scale.
WEIGHTS = {
    "industry_exposure": 23,
    "data_sensitivity": 22,
    "cloud_dependency": 12,
    "vendor_exposure": 14,
    "workforce_distribution": 10,
    "prior_incidents": 10,
    "regulatory_exposure": 14,
}

SECURITY_MATURITY_CREDITS = {
    "low": 0,
    "medium": 9,
    "high": 18,
}


def score_companies(companies: list[CompanyProfile]) -> list[ScoredCompany]:
    """Score a list of company profiles."""

    return [score_company(company) for company in companies]


def score_company(company: CompanyProfile) -> ScoredCompany:
    """Calculate the DEI score and underwriting outputs for one company."""

    breakdown = build_score_breakdown(company)
    score = round(max(0, min(100, breakdown.net_risk)), 1)
    risk_tier = classify_risk_tier(score)
    decision = underwriting_decision_for_tier(risk_tier)

    return ScoredCompany(
        profile=company,
        breakdown=breakdown,
        dei_score=score,
        risk_tier=risk_tier,
        underwriting_decision=decision,
        premium_range=premium_range_for_tier(risk_tier),
        estimated_risk_profile_summary=summarize_risk_profile(company, score, risk_tier, decision),
        key_risk_drivers=identify_key_risk_drivers(company, breakdown),
        recommended_mitigation_actions=recommend_mitigation_actions(company, risk_tier),
        explanation=explain_scoring_logic(company, breakdown, score, risk_tier, decision),
    )


def build_score_breakdown(company: CompanyProfile) -> ScoreBreakdown:
    """Build weighted risk components for one company."""

    return ScoreBreakdown(
        industry_exposure=WEIGHTS["industry_exposure"] * industry_factor(company.industry),
        data_sensitivity=WEIGHTS["data_sensitivity"]
        * level_factor(company.data_sensitivity, "data_sensitivity"),
        cloud_dependency=WEIGHTS["cloud_dependency"]
        * level_factor(company.cloud_dependency, "cloud_dependency"),
        vendor_exposure=WEIGHTS["vendor_exposure"]
        * level_factor(company.third_party_vendor_exposure, "third_party_vendor_exposure"),
        workforce_distribution=WEIGHTS["workforce_distribution"]
        * remote_workforce_factor(company.remote_workforce_percentage),
        prior_incidents=WEIGHTS["prior_incidents"]
        * historical_incident_factor(company.historical_incident_count),
        regulatory_exposure=WEIGHTS["regulatory_exposure"]
        * level_factor(company.regulatory_exposure, "regulatory_exposure"),
        security_maturity_credit=security_maturity_credit(company.security_maturity),
    )


def categorize_score(score: float) -> str:
    """Backward-compatible alias for risk tier classification."""

    return classify_risk_tier(score)


def level_factor(value: str, field_name: str) -> float:
    """Convert low/medium/high inputs into model factors."""

    normalized = value.strip().lower()

    if normalized not in LEVEL_FACTORS:
        expected = ", ".join(sorted(LEVEL_FACTORS))
        raise ValueError(f"{field_name} must be one of: {expected}")

    return LEVEL_FACTORS[normalized]


def industry_factor(industry: str) -> float:
    """Return inherent cyber exposure by industry."""

    normalized = industry.strip().lower()

    # Unknown industries receive a conservative middle-high default to preserve
    # portfolio scoring while still forcing underwriting attention.
    return INDUSTRY_RISK_FACTORS.get(normalized, 0.70)


def security_maturity_credit(security_maturity: str) -> float:
    """Return control credit from the organization's security maturity."""

    normalized = security_maturity.strip().lower()

    if normalized not in SECURITY_MATURITY_CREDITS:
        expected = ", ".join(sorted(SECURITY_MATURITY_CREDITS))
        raise ValueError(f"security_maturity must be one of: {expected}")

    return SECURITY_MATURITY_CREDITS[normalized]


def remote_workforce_factor(remote_workforce_percentage: int) -> float:
    """Convert remote workforce share into identity and endpoint exposure."""

    if remote_workforce_percentage < 0 or remote_workforce_percentage > 100:
        raise ValueError("remote_workforce_percentage must be from 0 to 100")

    if remote_workforce_percentage <= 20:
        return 0.20
    if remote_workforce_percentage <= 50:
        return 0.55
    if remote_workforce_percentage <= 75:
        return 0.80
    return 1.00


def historical_incident_factor(historical_incident_count: int) -> float:
    """Translate prior cyber losses into prospective underwriting concern."""

    if historical_incident_count < 0:
        raise ValueError("historical_incident_count cannot be negative")

    if historical_incident_count == 0:
        return 0.00
    if historical_incident_count == 1:
        return 0.45
    if historical_incident_count == 2:
        return 0.75
    return 1.00
