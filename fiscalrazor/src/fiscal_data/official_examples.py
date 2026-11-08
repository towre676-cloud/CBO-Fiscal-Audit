"""Official PUBLIC, INDIVIDUAL exemplars; NEVER a combined federal policy score.

CBO GDP nominal billion FY; SSA percentages of current-law OASDI taxable
payroll CY; JCT teaching example $bn ten-year mechanical adjustments.
"""
from pathlib import Path
from decimal import Decimal
import csv
BASE=Path(__file__).resolve().parents[2]
D=Decimal
OPTION_PATH=BASE/'data/verified_tables/ssa_individual_provision_annual_balance_2026_2036.csv'
JCT_PATH=BASE/'data/verified_tables/jct_2026_corporate_rate_teaching_example.csv'

def ssa_option_rows(path=OPTION_PATH):
 with open(path,newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
 if [int(r['calendar_year']) for r in rows]!=list(range(2026,2037)):raise ValueError('Incomplete SSA option calendar years')
 for row in rows:
  for key in ('E2_5','E1_10','B1_2'):
   val=D(row[key+'_delta_annual_balance_pct_payroll'])
   if not D(-5)<val<D(10):raise ValueError('Unreasonable SSA option percentage')
 if [D(r['B1_2_delta_annual_balance_pct_payroll']) for r in rows[:9]]!=[D(0)]*9:
  raise ValueError('B1.2 2033 cohort policy cannot produce early change')
 if D(rows[-1]['E2_5_delta_annual_balance_pct_payroll'])!=D('2.53'):
  raise ValueError('Official SSA E2.5 2036 benchmark mismatch')
 if D(rows[-1]['E1_10_delta_annual_balance_pct_payroll'])!=D('0.86'):
  raise ValueError('Official SSA E1.10 2036 benchmark mismatch')
 return rows

def actuarial_reference_2035_e25(payroll_bn=D('16486')):
 """SSA Table E2.5 % of current-law payroll x SSA intermediate CY2035 payroll.

 This is annual-balance improvement in CALENDAR YEAR 2035, not FY receipts.
 It does not include interaction with other policy options.
 """
 rows=ssa_option_rows();v=D(rows[9]['E2_5_delta_annual_balance_pct_payroll'])
 if payroll_bn!=D('16486'):raise ValueError('Unknown payroll source/vintage; do not extrapolate')
 return payroll_bn*v/D(100)

def jct_teaching_example(path=JCT_PATH):
 with open(path,newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
 if len(rows)!=10 or len(set(r['effect'] for r in rows))!=10:raise ValueError('JCT row count/identity mismatch')
 amount=sum((D(r['ten_year_effect_bn']) for r in rows),D(0))
 if amount!=D(180):raise ValueError('JCT teaching-example sum mismatch')
 if D(rows[0]['ten_year_effect_bn'])!=D(350):raise ValueError('JCT mechanical subtotal mismatch')
 return {'teaching_example_net_bn':amount,'mechanical_bn':D(rows[0]['ten_year_effect_bn']),
         'status':'JCT_ILLUSTRATIVE_NOT_OFFICIAL_SCORE', 'rows':rows}

def joint_ssa_estimate(*_args,**_kwargs):
 raise ValueError('UNSCORED: Cannot add single-option SSA annual balances to score a joint bill')

def joint_jct_estimate(*_args,**_kwargs):
 raise ValueError('UNSCORED: JCT teaching example is not a legislative score')
