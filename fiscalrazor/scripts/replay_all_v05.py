"""Run both original test suites and v0.5 cross-artifact checks, separately.

Report 101+53+7 executed test cases, not 161 unique independent scientific facts.
"""
from pathlib import Path
import subprocess,sys,json,re,os
ROOT=Path(__file__).resolve().parents[1]
CASES=[('FiscalRazor_v0.4 + v0.5 cross checks',ROOT, 'tests',108),
       ('Public scoring expansion separately preserved',ROOT/'external'/'public_scoring','tests',53)]
results=[]
for label,path,tests,expected in CASES:
    res=subprocess.run([sys.executable,'-m','unittest','discover','-s',tests,'-q'],
                       cwd=path,env={**os.environ,'PYTHONPATH':str(path/'src'),'PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    found=re.search(r'Ran (\d+) tests?',res.stdout)
    count=int(found.group(1)) if found else None
    results.append({'suite':label,'tests':count,'expected':expected,'passed':res.returncode==0 and count==expected,'detail':'OK' if res.returncode==0 and count==expected else res.stdout[-1000:]})
if any(not r['passed'] for r in results):
    print(json.dumps({'status':'FAIL','suites':results},indent=2));sys.exit(1)
sys.path.insert(0,str(ROOT/"src"))
from fiscal_data.reconcile_public import run_comparison
report={'status':'PASS_TESTED_SCOPES_NOT_OFFICIAL_POLICY_SCORE',
        'suites':results,'executed_test_cases':sum(r['tests'] for r in results),
        'cross_comparison':run_comparison(),
        'notes':['Some test cases overlap conceptually; counts are executed cases, not distinct independent validations.',
                 'Source-byte validation remains blocked pending original government archives.',
                 'All policy savings, household distribution and combined agency scoring remain UNSCORED.']}
(ROOT/'results'/'v05_reconciliation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
