"""BLS November 2026 correction instructions for 2025 Consumer Expenditure PUMD.

These deterministic functions are a documented recipe only. Real 2025 PUMD
has NOT been downloaded. Never apply these on already published/adjusted data.
"""
from __future__ import annotations
from decimal import Decimal
D=Decimal
INTERVIEW_MO_SCOPE={(2025,8):D('3.5'),(2025,9):D('5.5'),(2025,12):D('5.5'),(2026,1):D('3.5')}
MONTH_MULTIPLIER={7:D('1.5'),8:D(3),9:D(3),10:D('1.5')}

def interview_mo_scope(interview_year,interview_month,baseline_scope):
    if not 1<=int(interview_month)<=12:raise ValueError('INVALID_INTERVIEW_MONTH')
    scope=D(str(baseline_scope))
    if scope<=0 or not scope.is_finite():raise ValueError('INVALID_SCOPE')
    return INTERVIEW_MO_SCOPE.get((int(interview_year),int(interview_month)),scope)

def interview_2025_expenditure(expense_year,expense_month,amount,already_adjusted=False):
    if already_adjusted:raise ValueError('REFUSE_DOUBLE_ADJUSTMENT')
    if not 1<=int(expense_month)<=12:raise ValueError('INVALID_EXPENSE_MONTH')
    amount=D(str(amount))
    if not amount.is_finite():raise ValueError('INVALID_EXPENDITURE')
    factor=MONTH_MULTIPLIER.get(int(expense_month),D(1)) if int(expense_year)==2025 else D(1)
    return {'corrected_expenditure':amount*factor,'factor':factor,
            'scope':'BLS_2025_CE_PUMD_MISSING_MONTH_COMPENSATION'}

def diary_2025_weights(start_year,start_month,final_weight,replicate_weights,already_adjusted=False):
    if already_adjusted:raise ValueError('REFUSE_DOUBLE_ADJUSTMENT')
    if len(replicate_weights)!=44:raise ValueError('EXACTLY_44_DIARY_REPLICATE_WEIGHTS_REQUIRED')
    if not 1<=int(start_month)<=12:raise ValueError('INVALID_START_MONTH')
    factor=D(2) if int(start_year)==2025 and int(start_month) in (9,12) else D(1)
    values=[D(str(v)) for v in [final_weight,*replicate_weights]]
    if any(not v.is_finite() or v<0 for v in values):raise ValueError('INVALID_DIARY_WEIGHTS')
    return {'FINLWT21':factor*values[0], 'WTREP01_WTREP44':[factor*v for v in values[1:]],
            'multiplier':factor,'scope':'2025_CE_PUMD_MISSING_MONTH_WEIGHT_ADJUSTMENT'}
