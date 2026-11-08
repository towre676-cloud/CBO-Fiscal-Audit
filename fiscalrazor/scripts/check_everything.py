#!/usr/bin/env python3
from __future__ import annotations
import json,hashlib,os,sys,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from fiscal_data.accounting import verify_budget
from fiscal_data.actuarial import ssa_rows,trustee_key
from fiscal_data.acquisition import registry,inventory
from fiscal_data.accounting import read_direct_gdp
from fiscal_data.official_examples import ssa_option_rows,jct_teaching_example
from fiscal_data.medicare_cash import validate_hi,validate_smi
from fiscal_data.report import produce

checks={'cbo_fy':len(verify_budget()),'ssa_calendar_years':len(ssa_rows()),'trustfund_categories':len(trustee_key()),'registered_sources':len(registry()),'direct_gdp_years':len(read_direct_gdp()),'ssa_single_option_points':len(ssa_option_rows())*3,'jct_teaching_net_bn':str(jct_teaching_example()['teaching_example_net_bn']),'cms_hi_calendar_years':len(validate_hi()),'cms_smi_account_years':sum(len(q) for q in validate_smi().values()),'raw_sources_materialized':sum(x['status']=='MATERIALIZED_VERIFIED_BYTES' for x in inventory())}
print('CHECKED:',json.dumps(checks,sort_keys=True))
produce()
suite=unittest.defaultTestLoader.discover(str(BASE/'tests'))
result=unittest.TextTestRunner(verbosity=1).run(suite)
checks['unit_tests']=result.testsRun
checks['passed_tests']=result.testsRun-len(result.failures)-len(result.errors)
checks['state']='PASSED_INCLUDED_DATA_AND_SOFTWARE' if result.wasSuccessful() else 'FAILED'
(BASE/'results'/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
if not result.wasSuccessful():sys.exit(1)
