"""
LoanMate — ML Eligibility Predictor
=====================================
Rule-based scoring engine that produces a loan eligibility score (0–100)
and a recommendation for officer decision-support.

Design principles:
  - Pure Python. No external ML library dependencies at runtime.
  - No Django models, ORM queries, or database writes.
  - Read-only. Does NOT modify LoanApplication status.
  - Officers retain full authority. This is advisory only.

Scoring factors (total = 100 points):
  1. Credit Score     — max 35 pts
  2. Debt-to-Income   — max 30 pts
  3. Employment Type  — max 20 pts
  4. Income Level     — max 15 pts
"""


# ── Credit Score Factor (max 35 points) ──────────────────────────────────────

def _score_credit(credit_score: int) -> dict:
    """Score based on CIBIL/credit score bands."""
    if credit_score >= 750:
        pts = 35
        label = "Excellent (750+)"
    elif credit_score >= 700:
        pts = 28
        label = "Good (700–749)"
    elif credit_score >= 650:
        pts = 20
        label = "Fair (650–699)"
    elif credit_score >= 600:
        pts = 12
        label = "Poor (600–649)"
    else:
        pts = 0
        label = "Very Poor (<600)"

    return {"points": pts, "max": 35, "label": label}


# ── Debt-to-Income Factor (max 30 points) ────────────────────────────────────

def _estimate_monthly_emi(loan_amount: int, loan_tenure: int) -> float:
    """
    Estimate a flat monthly repayment (principal only).
    Avoids interest rate assumptions to keep the engine simple and auditable.
    """
    if loan_tenure <= 0:
        return float(loan_amount)
    return loan_amount / loan_tenure


def _score_dti(income: int, loan_amount: int, loan_tenure: int,
               existing_emi: int = 0) -> dict:
    """Score based on estimated debt-to-income ratio."""
    if income <= 0:
        return {"points": 0, "max": 30, "label": "No income data", "dti_pct": None}

    monthly_emi = _estimate_monthly_emi(loan_amount, loan_tenure)
    total_obligations = monthly_emi + existing_emi
    dti = (total_obligations / income) * 100

    if dti < 30:
        pts = 30
        label = f"Low DTI ({dti:.1f}%)"
    elif dti < 40:
        pts = 22
        label = f"Moderate DTI ({dti:.1f}%)"
    elif dti < 50:
        pts = 14
        label = f"High DTI ({dti:.1f}%)"
    else:
        pts = 0
        label = f"Very High DTI ({dti:.1f}%)"

    return {"points": pts, "max": 30, "label": label, "dti_pct": round(dti, 1)}


# ── Employment Type Factor (max 20 points) ───────────────────────────────────

_EMPLOYMENT_SCORES = {
    "salaried": 20,
    "full-time": 20,
    "full time": 20,
    "self-employed": 15,
    "self employed": 15,
    "business": 15,
    "part-time": 10,
    "part time": 10,
    "contract": 10,
    "freelance": 10,
    "unemployed": 5,
}


def _score_employment(employment_type: str) -> dict:
    """Score based on employment stability."""
    key = (employment_type or "").strip().lower()
    pts = _EMPLOYMENT_SCORES.get(key, 8)   # default modest score for unknowns
    label = employment_type or "Unknown"
    return {"points": pts, "max": 20, "label": label}


# ── Income Level Factor (max 15 points) ──────────────────────────────────────

def _score_income(income: int, loan_amount: int) -> dict:
    """Score based on income-to-loan ratio (how affordable the loan is)."""
    if income <= 0 or loan_amount <= 0:
        return {"points": 0, "max": 15, "label": "No data"}

    ratio = income / loan_amount  # monthly income / total loan

    if ratio >= 0.15:
        pts = 15
        label = "Very Strong Income"
    elif ratio >= 0.10:
        pts = 12
        label = "Strong Income"
    elif ratio >= 0.07:
        pts = 8
        label = "Adequate Income"
    elif ratio >= 0.05:
        pts = 4
        label = "Marginal Income"
    else:
        pts = 0
        label = "Insufficient Income"

    return {"points": pts, "max": 15, "label": label}


# ── Recommendation Thresholds ─────────────────────────────────────────────────

def _get_recommendation(score: int) -> dict:
    if score >= 70:
        return {
            "label": "APPROVE",
            "css_class": "approve",
            "icon": "fas fa-check-circle",
            "color": "#28a745",
            "message": "Applicant meets key eligibility criteria.",
        }
    elif score >= 50:
        return {
            "label": "BORDERLINE",
            "css_class": "borderline",
            "icon": "fas fa-exclamation-circle",
            "color": "#ffc107",
            "message": "Review carefully. Some risk factors present.",
        }
    else:
        return {
            "label": "REJECT",
            "css_class": "reject",
            "icon": "fas fa-times-circle",
            "color": "#dc3545",
            "message": "Significant eligibility concerns detected.",
        }


# ── Public API ────────────────────────────────────────────────────────────────

def predict(application) -> dict:
    """
    Compute an eligibility prediction for a LoanApplication instance.

    Args:
        application: A LoanApplication model instance. Read-only access.

    Returns:
        dict with keys:
          - score        (int, 0–100)
          - recommendation (dict with label, color, icon, message, css_class)
          - breakdown    (list of factor dicts for display)
          - bar_color    (str CSS color for the score gauge)
    """
    extra = application.extra_details or {}

    # Extract existing EMI from extra_details if present (Personal Loan)
    existing_emi = 0
    if extra.get("existing_emi"):
        try:
            existing_emi = int(extra.get("emi_amount", 0))
        except (ValueError, TypeError):
            existing_emi = 0

    # Calculate per-factor scores
    credit_factor = _score_credit(application.credit_score)
    dti_factor = _score_dti(
        income=application.income,
        loan_amount=application.loan_amount,
        loan_tenure=application.loan_tenure,
        existing_emi=existing_emi,
    )
    employment_factor = _score_employment(application.employment_type)
    income_factor = _score_income(application.income, application.loan_amount)

    # Total score
    total = (
        credit_factor["points"]
        + dti_factor["points"]
        + employment_factor["points"]
        + income_factor["points"]
    )

    # Bar color for score gauge
    if total >= 70:
        bar_color = "#28a745"
    elif total >= 50:
        bar_color = "#ffc107"
    else:
        bar_color = "#dc3545"

    recommendation = _get_recommendation(total)

    breakdown = [
        {
            "factor": "Credit Score",
            "icon": "fas fa-star",
            "label": credit_factor["label"],
            "points": credit_factor["points"],
            "max": credit_factor["max"],
        },
        {
            "factor": "Debt-to-Income",
            "icon": "fas fa-balance-scale",
            "label": dti_factor["label"],
            "points": dti_factor["points"],
            "max": dti_factor["max"],
        },
        {
            "factor": "Employment Type",
            "icon": "fas fa-briefcase",
            "label": employment_factor["label"],
            "points": employment_factor["points"],
            "max": employment_factor["max"],
        },
        {
            "factor": "Income Level",
            "icon": "fas fa-wallet",
            "label": income_factor["label"],
            "points": income_factor["points"],
            "max": income_factor["max"],
        },
    ]

    return {
        "score": total,
        "recommendation": recommendation,
        "breakdown": breakdown,
        "bar_color": bar_color,
    }


def predict_score(data: dict) -> dict:
    """
    Dict-based interface for standalone callers (tests, audit scripts, CLI).
    Does NOT require a Django model instance or ORM access.

    Expected keys:
        loan_type   (str)  — informational only, not used in scoring
        income      (int)  — monthly income
        employment  (str)  — employment type
        amount      (int)  — loan amount requested
        credit_score (int) — optional, defaults to 0 if absent
        loan_tenure  (int) — optional, defaults to 12 if absent

    Returns identical structure to predict():
        score, recommendation, breakdown, bar_color
    """
    income       = int(data.get("income", 0))
    loan_amount  = int(data.get("amount", 0))
    employment   = data.get("employment", "")
    credit_score = int(data.get("credit_score", 0))
    loan_tenure  = int(data.get("loan_tenure", 12))

    credit_factor     = _score_credit(credit_score)
    dti_factor        = _score_dti(income, loan_amount, loan_tenure)
    employment_factor = _score_employment(employment)
    income_factor     = _score_income(income, loan_amount)

    total = (
        credit_factor["points"]
        + dti_factor["points"]
        + employment_factor["points"]
        + income_factor["points"]
    )

    if total >= 70:
        bar_color = "#28a745"
    elif total >= 50:
        bar_color = "#ffc107"
    else:
        bar_color = "#dc3545"

    breakdown = [
        {"factor": "Credit Score",   "points": credit_factor["points"],     "max": credit_factor["max"],     "label": credit_factor["label"]},
        {"factor": "Debt-to-Income", "points": dti_factor["points"],        "max": dti_factor["max"],        "label": dti_factor["label"]},
        {"factor": "Employment",     "points": employment_factor["points"],  "max": employment_factor["max"], "label": employment_factor["label"]},
        {"factor": "Income Level",   "points": income_factor["points"],      "max": income_factor["max"],     "label": income_factor["label"]},
    ]

    return {
        "score": total,
        "recommendation": _get_recommendation(total),
        "breakdown": breakdown,
        "bar_color": bar_color,
    }
