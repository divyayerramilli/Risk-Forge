# Cyber Risk Underwriting Engine (Digital Exposure Index)

An explainable cyber risk underwriting engine that scores organizations using a Digital Exposure Index (DEI) and simulates how real underwriting decisions are made.

---

## Overview

Cyber underwriting is less about complex models and more about making fast, defensible decisions under uncertainty.

This project reflects how underwriting teams actually evaluate cyber risk. It uses transparent, factor-based scoring instead of black-box machine learning, allowing each decision to be understood, challenged, and refined.

The engine enables:

- Account-level cyber exposure scoring  
- Underwriting tier classification  
- Decision support (approve, approve with conditions, escalate, decline)  
- Portfolio-level risk analysis  
- Power BI-ready data outputs  
- Scenario simulation for risk improvement  

---

## Methodology

Each organization is evaluated across core cyber risk drivers:

- Industry exposure  
- Data sensitivity  
- Cloud dependency  
- Third-party vendor exposure  
- Workforce distribution  
- Prior cyber incidents  
- Regulatory exposure  
- Security maturity  

These inputs are combined into a 0–100 Digital Exposure Index (DEI), where higher scores indicate greater modeled exposure.

---

## Risk Logic

Risk is not evenly distributed across factors.

Industry exposure and data sensitivity carry the greatest weight due to their impact on breach likelihood, severity, and regulatory consequences.

Security maturity functions as a control-based adjustment. Strong controls reduce modeled exposure, while weaker environments receive little or no offset.

The model reflects real underwriting conditions:

- Exposure can accumulate across multiple dimensions  
- Controls can materially reduce risk  
- Final scores map directly to underwriting actions  

---

## Underwriting Framework

| DEI Score | Risk Tier | Decision |
|----------|----------|----------|
| 0–35 | Low | Approve |
| 35–60 | Moderate | Approve with Conditions |
| 60–80 | Elevated | Escalate for Review |
| 80–100 | Severe | Decline |

This structure mirrors how insurers triage and prioritize risk in practice.

---

## Portfolio Analytics

In addition to account-level scoring, the engine provides a portfolio view:

- Distribution of risk across tiers  
- Industry-level exposure trends  
- Key drivers of aggregate risk  
- Underwriting decision breakdown  

All outputs are structured for downstream analysis and dashboarding.

---

## Scenario Analysis

The model supports “what-if” scenarios commonly used in underwriting discussions:

- Improvements in security maturity  
- Changes in vendor exposure  
- Shifts in cloud or workforce reliance  

This allows risk assessment to transition into actionable improvement strategies.

---

## Run

```bash
python -m dei_underwriting
```

Outputs are generated as flat, analysis-ready files.

---

## Project Structure

```
dei_underwriting/
  scoring.py
  underwriting.py
  analytics.py
  scenario.py
  reporting.py
```

---

## Why This Project Matters

Cyber risk is complex, but underwriting decisions must remain clear and defensible.

This project demonstrates how to:

- Translate exposure signals into structured decisions  
- Maintain transparency in risk modeling  
- Align analytics with real business outcomes  

---

## Future Enhancements

- Configurable risk weights by insurer  
- Exposure-based premium modeling  
- Policy structure recommendations (limits, retention)  
- Integration with dashboard tools such as Power BI  
- Extension into claims and loss scenario modeling  
