def calculate_dti(monthly_income: float, total_monthly_debt: float) -> float:
    """
    Calculates the Debt-to-Income (DTI) ratio as a percentage.
    Lower is better.
    """
    if monthly_income <= 0:
        return 100.0
    return round((total_monthly_debt / monthly_income) * 100, 2)


def calculate_savings_rate(monthly_income: float, monthly_savings_contribution: float) -> float:
    """
    Calculates the percentage of income being saved each month.
    """
    if monthly_income <= 0:
        return 0.0
    return round((monthly_savings_contribution / monthly_income) * 100, 2)


def calculate_emergency_fund_coverage(total_savings: float, average_monthly_expenses: float) -> float:
    """
    Calculates how many months the user can survive on their current savings.
    """
    if average_monthly_expenses <= 0:
        return 0.0
    return round(total_savings / average_monthly_expenses, 1)


def evaluate_decision_risk(
        monthly_income: float,
        current_monthly_debt: float,
        new_monthly_obligation: float,
        savings_rate: float
) -> dict:
    """
    Rule-based risk assessment for major financial decisions based on current financial health[cite: 10].
    Evaluates risk level as Low, Moderate, or High[cite: 52].
    """
    projected_total_debt = current_monthly_debt + new_monthly_obligation
    projected_dti = calculate_dti(monthly_income, projected_total_debt)

    # Define thresholds for low-income households (~₹15,000 monthly income) [cite: 3]
    risk_level = "Low"

    if projected_dti > 40.0:
        risk_level = "High"
    elif projected_dti > 30.0 or savings_rate < 5.0:
        # If DTI is getting warm, or they aren't saving much, it's moderate risk
        risk_level = "Moderate"

    return {
        "projected_dti": projected_dti,
        "risk_level": risk_level
    }