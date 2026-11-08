"""One explicitly dated 2035 OASDI taxable-payroll cross-source computation.

These are derived calendar-year changes to an OASDI actuarial balance (NOT
Federal FY deficit savings). Rounding in SSA published percentages matters.
"""
from decimal import Decimal as D
from .fiscalrazor import ssa_option_series

# 2026 OASDI Trustees Report, IV.A Short Range narrative, Intermediate case.
# https://www.ssa.gov/oact/tr/2026/IV_A_SRest.html
# Source wording: "total taxable payroll ... $16,486 billion ... in 2035"
CL_TAXABLE_PAYROLL_CY2035_BILLION = D('16486')


def approximate_ssa_cy2035_balance_change(option_id):
    rate_pp = dict(ssa_option_series(option_id))[2035]
    annual = CL_TAXABLE_PAYROLL_CY2035_BILLION * rate_pp/D(100)
    # Percent displayed with 2 decimals -> ± 0.005 percentage points, plus
    # published taxable payroll rounded to nearest billion, not captured here.
    pct_rounding_bound = CL_TAXABLE_PAYROLL_CY2035_BILLION * D('0.005')/D(100)
    return dict(calendar_year=2035,option_id=option_id,
        payroll_billion=str(CL_TAXABLE_PAYROLL_CY2035_BILLION),
        official_annual_balance_change_pct_of_cl_payroll=str(rate_pp),
        derived_annual_actuarial_balance_improvement_billion=str(annual),
        pct_rounding_only_uncertainty_bound_billion=str(pct_rounding_bound),
        status='DERIVED_FROM_SSA_TABLES_NOT_FY_CASH_NOT_OFFICIAL_DOLLAR_SCORE',
        sources=['https://www.ssa.gov/oact/tr/2026/IV_A_SRest.html',
          'https://www.ssa.gov/oact/solvency/provisions/tables/table_run214.html'])
