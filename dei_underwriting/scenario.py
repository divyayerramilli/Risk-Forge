"""Scenario simulation and sensitivity analysis tools."""

from dataclasses import replace

from .models import CompanyProfile, ScenarioResult, SensitivityResult
from .scoring import score_company


LEVEL_ORDER = ["low", "medium", "high"]


def simulate_security_maturity_improvement(
    companies: list[CompanyProfile],
    target_maturity: str = "high",
) -> list[ScenarioResult]:
    """Simulate all accounts improving to a target security maturity level."""

    scenario_results = []

    for company in companies:
        adjusted = replace(company, security_maturity=target_maturity)
        scenario_results.append(_scenario_result(company, adjusted, "Security maturity improves to high"))

    return scenario_results


def simulate_remote_workforce_decrease(
    companies: list[CompanyProfile],
    reduction_points: int = 25,
    floor: int = 10,
) -> list[ScenarioResult]:
    """Simulate reduced remote workforce exposure."""

    scenario_results = []

    for company in companies:
        adjusted_remote = max(floor, company.remote_workforce_percentage - reduction_points)
        adjusted = replace(company, remote_workforce_percentage=adjusted_remote)
        scenario_results.append(_scenario_result(company, adjusted, "Remote workforce exposure decreases"))

    return scenario_results


def run_sensitivity_analysis(companies: list[CompanyProfile]) -> list[SensitivityResult]:
    """Run one-factor sensitivity tests for major underwriting risk drivers."""

    results = []

    for company in companies:
        baseline = score_company(company)
        scenarios = [
            (
                "Security maturity",
                _improve_security_maturity(company),
                "Improve maturity by one level where possible.",
            ),
            (
                "Vendor exposure",
                replace(
                    company,
                    third_party_vendor_exposure=_decrease_level(company.third_party_vendor_exposure),
                ),
                "Reduce vendor exposure by one level where possible.",
            ),
            (
                "Cloud dependency",
                replace(company, cloud_dependency=_decrease_level(company.cloud_dependency)),
                "Reduce cloud dependency by one level where possible.",
            ),
            (
                "Remote workforce",
                replace(
                    company,
                    remote_workforce_percentage=max(0, company.remote_workforce_percentage - 25),
                ),
                "Reduce remote workforce exposure by 25 percentage points.",
            ),
            (
                "Prior incidents",
                replace(
                    company,
                    historical_incident_count=max(0, company.historical_incident_count - 1),
                ),
                "Model one fewer historical incident after remediation evidence.",
            ),
        ]

        for factor, adjusted_company, note in scenarios:
            adjusted = score_company(adjusted_company)
            results.append(
                SensitivityResult(
                    company_name=company.company_name,
                    factor=factor,
                    baseline_score=baseline.dei_score,
                    adjusted_score=adjusted.dei_score,
                    score_change=round(adjusted.dei_score - baseline.dei_score, 1),
                    note=note,
                )
            )

    return results


def _scenario_result(
    baseline_company: CompanyProfile,
    adjusted_company: CompanyProfile,
    scenario_name: str,
) -> ScenarioResult:
    baseline = score_company(baseline_company)
    adjusted = score_company(adjusted_company)

    return ScenarioResult(
        company_name=baseline_company.company_name,
        scenario_name=scenario_name,
        baseline_score=baseline.dei_score,
        scenario_score=adjusted.dei_score,
        score_change=round(adjusted.dei_score - baseline.dei_score, 1),
        baseline_tier=baseline.risk_tier,
        scenario_tier=adjusted.risk_tier,
        baseline_decision=baseline.underwriting_decision,
        scenario_decision=adjusted.underwriting_decision,
    )


def _improve_security_maturity(company: CompanyProfile) -> CompanyProfile:
    current = company.security_maturity.lower()
    current_index = LEVEL_ORDER.index(current)
    improved = LEVEL_ORDER[min(current_index + 1, len(LEVEL_ORDER) - 1)]
    return replace(company, security_maturity=improved)


def _decrease_level(value: str) -> str:
    current = value.lower()
    current_index = LEVEL_ORDER.index(current)
    return LEVEL_ORDER[max(current_index - 1, 0)]
