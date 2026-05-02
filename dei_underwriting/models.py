"""Domain models for the Digital Exposure Index Risk Engine."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CompanyProfile:
    """Company inputs used by the underwriting risk model."""

    company_name: str
    industry: str
    annual_revenue: int
    employee_count: int
    data_sensitivity: str
    cloud_dependency: str
    remote_workforce_percentage: int
    third_party_vendor_exposure: str
    security_maturity: str
    historical_incident_count: int
    regulatory_exposure: str

    @property
    def cloud_usage(self) -> str:
        """Backward-compatible alias for the earlier project version."""

        return self.cloud_dependency

    @property
    def remote_workforce(self) -> int:
        """Backward-compatible alias for the earlier project version."""

        return self.remote_workforce_percentage

    @property
    def vendor_exposure(self) -> str:
        """Backward-compatible alias for the earlier project version."""

        return self.third_party_vendor_exposure


@dataclass(frozen=True)
class ScoreBreakdown:
    """Weighted scoring components before the maturity mitigation credit."""

    industry_exposure: float
    data_sensitivity: float
    cloud_dependency: float
    vendor_exposure: float
    workforce_distribution: float
    prior_incidents: float
    regulatory_exposure: float
    security_maturity_credit: float

    @property
    def gross_risk(self) -> float:
        """Risk before applying the security maturity mitigation credit."""

        return sum(self.positive_components().values())

    @property
    def net_risk(self) -> float:
        """Risk after applying the security maturity mitigation credit."""

        return self.gross_risk - self.security_maturity_credit

    def positive_components(self) -> dict[str, float]:
        """Return the positive exposure drivers."""

        return {
            "industry_exposure": self.industry_exposure,
            "data_sensitivity": self.data_sensitivity,
            "cloud_dependency": self.cloud_dependency,
            "vendor_exposure": self.vendor_exposure,
            "workforce_distribution": self.workforce_distribution,
            "prior_incidents": self.prior_incidents,
            "regulatory_exposure": self.regulatory_exposure,
        }

    def all_components(self) -> dict[str, float]:
        """Return positive risk drivers plus the maturity control credit."""

        return {
            **self.positive_components(),
            "security_maturity_credit": -self.security_maturity_credit,
        }


@dataclass(frozen=True)
class ScoredCompany:
    """Full underwriting result for one account."""

    profile: CompanyProfile
    breakdown: ScoreBreakdown
    dei_score: float
    risk_tier: str
    underwriting_decision: str
    premium_range: str
    estimated_risk_profile_summary: str
    key_risk_drivers: list[str]
    recommended_mitigation_actions: list[str]
    explanation: str

    @property
    def digital_exposure_index(self) -> float:
        """Backward-compatible alias for the earlier project version."""

        return self.dei_score

    @property
    def risk_category(self) -> str:
        """Backward-compatible alias for the earlier project version."""

        return self.risk_tier


@dataclass(frozen=True)
class ScenarioResult:
    """Before-and-after result for a simulated underwriting scenario."""

    company_name: str
    scenario_name: str
    baseline_score: float
    scenario_score: float
    score_change: float
    baseline_tier: str
    scenario_tier: str
    baseline_decision: str
    scenario_decision: str


@dataclass(frozen=True)
class SensitivityResult:
    """One-factor sensitivity result for a company."""

    company_name: str
    factor: str
    baseline_score: float
    adjusted_score: float
    score_change: float
    note: str
