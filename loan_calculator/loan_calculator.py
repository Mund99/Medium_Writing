def calculate_eir_guess_balance(eir_guess, total_loan, monthly_installment, tenure_yr):
    """
    Calculate the remaining balance based on the guessed Effective Interest Rate (EIR).

    Parameters:
    - eir_guess (float): Guessed Effective Interest Rate.
    - total_loan (float): Total loan amount.
    - monthly_installment (float): Monthly installment.
    - tenure_mth (int): Total number of months in the loan tenure.

    Returns:
    float: Remaining balance based on the guessed EIR.
    """
    interest_balance = total_loan
    for _ in range(tenure_yr*12):
        interest = interest_balance * eir_guess / 12
        interest_balance = interest_balance + interest - monthly_installment
    return interest_balance

def find_effective_interest_rate(total_loan, monthly_installment, tenure_yr, interest_rate, tolerance=0.000001, max_iterations=10000):
    """
    Find the Effective Interest Rate (EIR) using an iterative method.

    Parameters:
    - total_loan (float): Total loan amount.
    - monthly_installment (float): Monthly installment.
    - tenure_yr (int): Loan tenure in years.
    - tolerance (float): Tolerance level for convergence.
    - max_iterations (int): Maximum number of iterations.

    Returns:
    float or None: Found EIR or None if convergence fails within the specified iterations.
    """
    eir_guess = interest_rate / 100
    eir_guess_balance = total_loan
    iterations = 0

    while iterations < max_iterations:
        eir_guess_balance = calculate_eir_guess_balance(eir_guess, total_loan, monthly_installment, tenure_yr)

        # Adjust guessed EIR based on the balance
        increment_factor = min(1.0, abs(eir_guess_balance) / total_loan)
        increment = 0.01 * increment_factor

        if eir_guess_balance < 0:
            eir_guess += increment
        else:
            eir_guess -= increment

        if abs(eir_guess_balance) <= tolerance:
            # print(f"Found EIR: {(eir_guess*100):.2f}% after {iterations + 1} iterations.")
            return eir_guess

        iterations += 1

    # print("Failed to converge.")
    return None

def calculate_loan_metrics(total_loan, tenure_yr, interest_rate):
    
    # Calculate derived values
    tenure_mth = tenure_yr * 12
    total_interest = (interest_rate / 100) * total_loan * tenure_yr
    yearly_interest = total_interest / tenure_yr
    monthly_interest = yearly_interest / 12
    monthly_installment = (total_loan + total_interest) / tenure_mth
    total_repayment = total_loan + total_interest

    # Use your existing function to find the effective interest rate
    effective_interest_rate = find_effective_interest_rate(total_loan, monthly_installment, tenure_yr, interest_rate)

    return monthly_installment, total_repayment, effective_interest_rate
