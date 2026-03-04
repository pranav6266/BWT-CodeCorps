from typing import Optional


DTI_HIGH_THRESHOLD = 40.0
DTI_MODERATE_THRESHOLD = 30.0
SAVINGS_RATE_LOW_THRESHOLD = 5.0
EMERGENCY_FUND_RECOMMENDED_MONTHS = 3.0


def calculate_dti(monthly_income: float, total_monthly_debt: float) -> float:
    """
    Calculates the Debt-to-Income (DTI) ratio as a percentage.
    Lower is better.
    """
    if monthly_income <= 0:
        return 100.0
    if total_monthly_debt < 0:
        total_monthly_debt = 0
    return round((total_monthly_debt / monthly_income) * 100, 2)


def calculate_savings_rate(
    monthly_income: float, monthly_savings_contribution: float
) -> float:
    """
    Calculates the percentage of income being saved each month.
    """
    if monthly_income <= 0:
        return 0.0
    if monthly_savings_contribution < 0:
        return 0.0
    savings = round((monthly_savings_contribution / monthly_income) * 100, 2)
    return min(savings, 100.0)


def calculate_emergency_fund_coverage(
    total_savings: float, average_monthly_expenses: float
) -> float:
    """
    Calculates how many months the user can survive on their current savings.
    """
    if average_monthly_expenses <= 0:
        return 0.0
    if total_savings < 0:
        return 0.0
    return round(total_savings / average_monthly_expenses, 1)


def calculate_disposable_income(
    monthly_income: float, total_expenses: float, monthly_debt: float
) -> float:
    """
    Calculates monthly disposable income (money left after expenses and debt).
    """
    if monthly_income <= 0:
        return 0.0
    if total_expenses < 0:
        total_expenses = 0
    if monthly_debt < 0:
        monthly_debt = 0

    disposable = monthly_income - total_expenses - monthly_debt
    return round(max(0.0, disposable), 2)


def check_emergency_fund_status(monthly_expenses: float, total_savings: float) -> dict:
    """
    Checks emergency fund status and returns recommendations.
    """
    coverage_months = calculate_emergency_fund_coverage(total_savings, monthly_expenses)

    if coverage_months >= 6:
        status = "excellent"
        message = "You have an excellent emergency fund (6+ months)"
    elif coverage_months >= 3:
        status = "good"
        message = "You have a good emergency fund (3-6 months)"
    elif coverage_months >= 1:
        status = "insufficient"
        message = "Your emergency fund needs building (1-3 months)"
    else:
        status = "critical"
        message = "No emergency fund - highly recommended to build one"

    return {
        "status": status,
        "coverage_months": coverage_months,
        "message": message,
    }


def calculate_risk_score(
    projected_dti: float,
    savings_rate: float,
    disposable_income: float,
    monthly_income: float,
) -> int:
    """
    Calculates a numeric risk score from 0 (lowest risk) to 100 (highest risk).
    """
    if monthly_income <= 0:
        return 100

    score = 0

    if projected_dti > 50:
        score += 60
    elif projected_dti > 40:
        score += 50
    elif projected_dti > 30:
        score += 30
    elif projected_dti > 20:
        score += 15
    else:
        score += 0

    if savings_rate < 3:
        score += 25
    elif savings_rate < 5:
        score += 15
    elif savings_rate < 10:
        score += 5

    if disposable_income < 0:
        score += 20
    elif disposable_income < (monthly_income * 0.1):
        score += 10

    return min(100, max(0, score))


def get_risk_factors(
    projected_dti: float,
    current_dti: float,
    savings_rate: float,
    projected_monthly_expenses: float,
    monthly_income: float,
) -> list[str]:
    """
    Returns a list of specific risk factors identified.
    """
    factors = []

    if projected_dti > DTI_HIGH_THRESHOLD:
        factors.append(
            f"Very high projected DTI ({projected_dti}%) exceeds {DTI_HIGH_THRESHOLD}% threshold"
        )
    elif projected_dti > DTI_MODERATE_THRESHOLD:
        factors.append(
            f"High projected DTI ({projected_dti}%) exceeds {DTI_MODERATE_THRESHOLD}% threshold"
        )

    if current_dti > DTI_HIGH_THRESHOLD:
        factors.append(f"Current DTI ({current_dti}%) is already high")

    if savings_rate < SAVINGS_RATE_LOW_THRESHOLD:
        factors.append(
            f"Low savings rate ({savings_rate}%) below {SAVINGS_RATE_LOW_THRESHOLD}% recommended"
        )

    if projected_monthly_expenses > (monthly_income * 0.9):
        factors.append("Projected expenses would use over 90% of income")

    if savings_rate == 0:
        factors.append("No current savings - financially vulnerable")

    return factors


def get_warnings(
    projected_dti: float,
    current_dti: float,
    savings_rate: float,
) -> list[str]:
    """
    Returns warnings for borderline risk cases.
    """
    warnings = []

    if 28 <= projected_dti < DTI_MODERATE_THRESHOLD:
        warnings.append(f"DTI is approaching moderate risk zone ({projected_dti}%)")

    if 3 <= savings_rate < SAVINGS_RATE_LOW_THRESHOLD:
        warnings.append(f"Savings rate is borderline low ({savings_rate}%)")

    if current_dti > 0 and projected_dti > current_dti:
        dti_increase = projected_dti - current_dti
        if dti_increase > 10:
            warnings.append(
                f"This decision would increase your DTI by {dti_increase:.1f}%"
            )

    return warnings


def evaluate_decision_risk(
    monthly_income: float,
    current_monthly_debt: float,
    new_monthly_obligation: float,
    savings_rate: float,
    current_total_expenses: float = 0,
    total_savings: float = 0,
) -> dict:
    """
    Rule-based risk assessment for major financial decisions based on current financial health.
    Evaluates risk level as Low, Moderate, or High.

    Args:
        monthly_income: User's monthly income
        current_monthly_debt: Current monthly debt obligations
        new_monthly_obligation: New monthly obligation from the decision
        savings_rate: Current savings rate percentage
        current_total_expenses: Optional - total monthly expenses for emergency fund check
        total_savings: Optional - total savings for emergency fund check

    Returns:
        Dictionary with risk_level, projected_dti, risk_score, risk_factors, warnings
    """
    if monthly_income <= 0:
        return {
            "projected_dti": 100.0,
            "risk_level": "High",
            "risk_score": 100,
            "risk_factors": ["No valid income provided"],
            "warnings": ["Please set up your financial profile with valid income"],
        }

    if new_monthly_obligation < 0:
        new_monthly_obligation = 0
    if current_monthly_debt < 0:
        current_monthly_debt = 0
    if savings_rate < 0:
        savings_rate = 0

    projected_total_debt = current_monthly_debt + new_monthly_obligation
    projected_dti = calculate_dti(monthly_income, projected_total_debt)
    current_dti = calculate_dti(monthly_income, current_monthly_debt)

    projected_monthly_expenses = current_total_expenses + new_monthly_obligation
    disposable_income = calculate_disposable_income(
        monthly_income, current_total_expenses, current_monthly_debt
    )

    risk_level = "Low"

    if projected_dti > DTI_HIGH_THRESHOLD:
        risk_level = "High"
    elif (
        projected_dti > DTI_MODERATE_THRESHOLD
        or savings_rate < SAVINGS_RATE_LOW_THRESHOLD
    ):
        risk_level = "Moderate"

    risk_score = calculate_risk_score(
        projected_dti, savings_rate, disposable_income, monthly_income
    )

    risk_factors = get_risk_factors(
        projected_dti,
        current_dti,
        savings_rate,
        projected_monthly_expenses,
        monthly_income,
    )

    warnings = get_warnings(projected_dti, current_dti, savings_rate)

    return {
        "projected_dti": projected_dti,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "warnings": warnings,
    }
