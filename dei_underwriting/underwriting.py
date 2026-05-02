"""Underwriting decision logic for the DEI Risk Engine."""

from .models import CompanyProfile, ScoreBreakdown


TIER_BOUNDARIES = {
    "Low": (0, 35),
    "Moderate": (35.1, 60),
    "Elevated": (60.1, 80),
    "Severe": (80.1, 100),
}

UNDERWRITING_DECISIONS = {
    "Low": "Approve",
    "Moderate": "Approve with Conditions",
    "Elevated": "Escalate for Manual Review",
    "Severe": "Decline",
}

PREMIUM_RANGES = {
    "Low": "$15K-$50K",
    "Moderate": "$50K-$150K",
    "Elevated": "$150K-$400K",
    "Severe": "$400K+ or referral-only pricing",
}


def classify_risk_tier(score: float) -> str:
    """Classify a 0-100 DEI score into an underwriting risk tier."""

    if score <= 35:
        return "Low"
    if score <= 60:
        return "Moderate"
    if score <= 80:
        return "Elevated"
    return "Severe"


def underwriting_decision_for_tier(risk_tier: str) -> str:
    """Return the underwriting decision for a risk tier."""

    return UNDERWRITING_DECISIONS[risk_tier]


def premium_range_for_tier(risk_tier: str) -> str:
    """Return an indicative premium range for demo and portfolio analytics."""

    return PREMIUM_RANGES[risk_tier]


def summarize_risk_profile(
    company: CompanyProfile,
    score: float,
    risk_tier: str,
    decision: str,
) -> str:
    """Create an executive-friendly risk profile summary."""

    scale = _company_size_label(company)
    return (
        f"{company.company_name} is a {scale} {company.industry} account with a DEI score "
        f"of {score:.1f}. The account is classified as {risk_tier}, resulting in an "
        f"underwriting posture of {decision}."
    )


def identify_key_risk_drivers(
    company: CompanyProfile,
    breakdown: ScoreBreakdown,
    limit: int = 4,
) -> list[str]:
    """Return the strongest underwriting risk drivers for an account."""

    driver_labels = {
        "industry_exposure": f"{company.industry} industry exposure",
        "data_sensitivity": f"{company.data_sensitivity} data sensitivity",
        "cloud_dependency": f"{company.cloud_dependency} cloud dependency",
        "vendor_exposure": f"{company.third_party_vendor_exposure} third-party vendor exposure",
        "workforce_distribution": f"{company.remote_workforce_percentage}% remote workforce",
        "prior_incidents": f"{company.historical_incident_count} historical cyber incident(s)",
        "regulatory_exposure": f"{company.regulatory_exposure} regulatory exposure",
    }

    ranked = sorted(
        breakdown.positive_components().items(),
        key=lambda item: item[1],
        reverse=True,
    )
    drivers = [driver_labels[key] for key, value in ranked if value > 0][:limit]

    if company.security_maturity.lower() == "low":
        drivers.append("limited security maturity control evidence")

    return drivers[:limit]


def recommend_mitigation_actions(company: CompanyProfile, risk_tier: str) -> list[str]:
    """Map risk profile inputs to underwriting-oriented mitigation actions."""

    actions = []

    if company.security_maturity.lower() == "low":
        actions.append("Require MFA coverage, endpoint detection, backup testing, and incident response planning.")
    elif company.security_maturity.lower() == "medium":
        actions.append("Validate control effectiveness through recent security assessments and tabletop exercises.")

    if company.third_party_vendor_exposure.lower() == "high":
        actions.append("Strengthen vendor due diligence, contract security clauses, and critical vendor monitoring.")

    if company.cloud_dependency.lower() == "high":
        actions.append("Review cloud identity controls, logging coverage, encryption, and configuration posture.")

    if company.remote_workforce_percentage > 50:
        actions.append("Tighten remote access controls, device posture checks, and privileged access management.")

    if company.historical_incident_count >= 2:
        actions.append("Request loss history details and evidence that prior incident remediation is complete.")

    if company.regulatory_exposure.lower() == "high":
        actions.append("Confirm privacy governance, breach notification processes, and regulatory compliance controls.")

    if risk_tier == "Severe":
        actions.append("Move to senior referral with possible sublimits, exclusions, or declination.")
    elif risk_tier == "Elevated":
        actions.append("Consider higher retention, ransomware sublimits, and pre-bind control conditions.")

    return actions or ["Maintain current controls and monitor for material exposure changes at renewal."]


def explain_scoring_logic(
    company: CompanyProfile,
    breakdown: ScoreBreakdown,
    score: float,
    risk_tier: str,
    decision: str,
) -> str:
    """Build transparent scoring rationale for underwriting review."""

    top_drivers = identify_key_risk_drivers(company, breakdown, limit=3)

    if breakdown.security_maturity_credit > 0:
        control_text = (
            f"{company.security_maturity.capitalize()} security maturity reduced modeled risk by "
            f"{breakdown.security_maturity_credit:.1f} points"
        )
    else:
        control_text = "Low security maturity provided no material risk reduction"

    return (
        f"Top risk drivers were {', '.join(top_drivers)}. {control_text}. "
        f"The final DEI score of {score:.1f} maps to the {risk_tier} tier, so the "
        f"recommended underwriting decision is {decision}."
    )


def _company_size_label(company: CompanyProfile) -> str:
    if company.annual_revenue >= 1_000_000_000 or company.employee_count >= 5_000:
        return "large-enterprise"
    if company.annual_revenue >= 250_000_000 or company.employee_count >= 1_000:
        return "middle-market"
    return "small-commercial"
