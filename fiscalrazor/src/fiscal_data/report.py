from __future__ import annotations
import csv,html,json
from decimal import Decimal
from pathlib import Path
from .accounting import verify_budget,read_budget,target_gap_2036,read_actual
from .actuarial import ssa_rows,trustee_key
from .acquisition import inventory,BASE
from .reconciliation import events
from .official_examples import ssa_option_rows,jct_teaching_example
from .medicare_cash import validate_hi,validate_smi

RESULTS=BASE/'results'

def produce():
 RESULTS.mkdir(exist_ok=True)
 fiscal=verify_budget();ssa=ssa_rows();trustee=trustee_key();source_inventory=inventory()
 with (RESULTS/'verified_baseline_2026_2036.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(fiscal[0]));w.writeheader();w.writerows(fiscal)
 with (RESULTS/'source_acquisition_inventory.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(source_inventory[0]));w.writeheader();w.writerows(source_inventory)
 gap=target_gap_2036()
 (RESULTS/'objective_2036.json').write_text(json.dumps({k:(str(v) if isinstance(v,Decimal) else v) for k,v in gap.items()},indent=2)+'\n')
 actual=read_actual();b=read_budget()
 (RESULTS/'verification_status.json').write_text(json.dumps({
  'status_date':'2026-11-06','accounting':{'status':'CHECKED_INCLUDED_CBO_DATA','years':len(fiscal),'selected_source_cells':sum(len(v) for v in b.values())},
  'ssa':{'status':'CHECKED_TRANSCRIBED_2026_SINGLE_YEAR_TABLE_IVB1','years':len(ssa),
         'single_provision_option_points':len(ssa_option_rows())*3,'joint_reform_status':'UNSCORED'},
  'jct':{'status':'CHECKED_PUBLISHED_TEACHING_EXAMPLE_NOT_OFFICIAL_SCORE','illustrative_net_bn':str(jct_teaching_example()['teaching_example_net_bn'])},
  'cms_2026':{'status':'PUBLISHED_HI_SMI_ANNUAL_TABLES_TRANSCRIBED_AND_ACCOUNTING_CHECKED_NOT_FULL_ORIGINAL_ZIP','hi_calendar_years':len(validate_hi()),'smi_account_years':sum(len(s) for s in validate_smi().values()),'combined_reform_score':'NOT_AVAILABLE'},
  'raw_dataset_acquisition':{'fully_downloaded':sum(x['status']=='MATERIALIZED_VERIFIED_BYTES' for x in source_inventory),'registered':len(source_inventory),'note':'The materialized CBO/SSA tables are selected extracts, not the complete raw data releases.'},
  'official_combined_score':'NOT_AVAILABLE','household_reform_incidence':'NOT_COMPUTABLE_NO_RAW_HOUSEHOLD_AND_REFORM_RECORDS',
  'new_annual_baseline_after_tariff_update':'NOT_AVAILABLE',
  'fy2026_actual_difference_bn':str(Decimal(actual['deficit_bn'])+b[2026]['proj_deficit_total'])},indent=2)+'\n')
 _html(fiscal,ssa,trustee,source_inventory,gap,actual)
 print('reports created, registered sources:',len(source_inventory))

def _html(fiscal,ssa,trustee,catalog,gap,actual):
 def f(x,n=1):return f'{float(x):,.{n}f}'
 table_fiscal=''.join('<tr>'+'<td>'+str(r['year'])+'</td>'+'<td>'+f(r['deficit_bn'])+'</td>'+'<td>'+f(r['primary_deficit_bn'])+'</td>'+'<td>'+f(r['net_interest_bn'])+'</td>'+'<td>'+f(r['debt_bn'])+'</td>'+'<td>'+f(r['debt_pct_gdp'])+'%</td></tr>' for r in fiscal)
 table_ssa=''.join('<tr><td>'+r['year']+'</td><td>'+r['oasi_income_pct']+'</td><td>'+r['oasi_cost_pct']+'</td><td>'+r['oasi_balance_pct']+'</td><td>'+r['di_balance_pct']+'</td><td>'+r['combined_oasdi_balance_pct']+'</td></tr>' for r in ssa)
 table_catalog=''.join('<tr><td>'+html.escape(x['id'])+'</td><td>'+html.escape(x['agency'])+'</td><td>'+html.escape(x['status'])+'</td><td><a href="'+html.escape(x['source_url'])+'" target="_blank" rel="noopener noreferrer">Official source</a></td></tr>' for x in catalog)
 text=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FiscalRazor · Data Foundation</title>
<style>:root{{--bg:#f8f7f2;--fg:#19252a;--muted:#60717a;--blue:#165b87;--accent:#b8723b;--border:#d5d8d7}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,Segoe UI,Arial,sans-serif}}header{{background:#152c3b;color:#fff;padding:40px max(5%,calc((100vw - 1150px)/2))}}header h1{{font-size:clamp(27px,5vw,44px);margin:0}}header p{{color:#cbdce4;max-width:900px}}.tag{{font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:11px}}main{{max-width:1150px;margin:auto;padding:18px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:25px 0}}.card{{background:white;border:1px solid var(--border);border-radius:12px;padding:20px}}.card strong{{display:block;font-size:clamp(22px,3vw,31px);color:var(--blue)}}.card small{{color:var(--muted)}}.note{{padding:15px 20px;border-left:4px solid var(--accent);background:#fff;margin:18px 0}}section{{margin:32px 0}}h2{{margin-bottom:10px;font-size:24px}}.twrap{{overflow-x:auto;border:1px solid var(--border);border-radius:8px;background:white}}table{{width:100%;border-collapse:collapse;white-space:nowrap;font-variant-numeric:tabular-nums}}td,th{{padding:11px 13px;border-bottom:1px solid #e8eaea;text-align:right}}th{{position:sticky;top:0;background:#eaf1f5;color:#173749;font-size:13px}}td:first-child,th:first-child{{text-align:left}}tr:hover td{{background:#f1f6f7}}a{{color:#0c689e}}.footer{{color:var(--muted);font-size:13px}}input{{font-size:16px;padding:10px;border-radius:8px;border:1px solid var(--border);max-width:100%;width:360px}}</style></head><body>
<header><div class="tag">Source-grounded federal data · 2026-11-06</div><h1>FiscalRazor Data Foundation</h1><p>Verified fiscal accounting, SSA actuarial table, source acquisition ledger, and explicit official-score and household-incidence gates. No estimated reform savings are presented.</p></header>
<main><div class="cards"><div class="card"><small>CBO FY2036 deficit</small><strong>${f(fiscal[-1]['deficit_bn'])}B</strong><small>February 2026 projection</small></div><div class="card"><small>FY2036 net interest</small><strong>${f(fiscal[-1]['net_interest_bn'])}B</strong><small>Public debt servicing projection</small></div><div class="card"><small>3% deficit target shortfall</small><strong>${f(gap['gap_bn'])}B</strong><small>Static accounting target only</small></div><div class="card"><small>Indexed source registry</small><strong>{len(catalog)} entries</strong><small>{len(fiscal)} CBO yearly observations; {len(ssa)} SSA annual rows</small></div></div>
<div class="note"><strong>Data status:</strong> Selected official-source extracts are materialized; direct published fiscal-year GDP and three SSA individual options plus a JCT teaching illustration are added. Large source archives listed below are <strong>not yet downloaded here</strong>. Household reform incidence and officially scored combined legislative effects have not been established. CBO's August tariff adjustment is separate from the February baseline.</div>
<section><h2>Federal budget · CBO February 2026</h2><p>Money in billions of nominal dollars. The deficit column displays a positive shortfall; CBO's raw deficit data use the negative convention. Total spending is reconciled to receipts and the debt financing residual.</p><div class="twrap"><table><thead><tr><th>Fiscal year</th><th>Deficit ($B)</th><th>Primary ($B)</th><th>Interest ($B)</th><th>Public debt ($B)</th><th>Debt/GDP</th></tr></thead><tbody>{table_fiscal}</tbody></table></div></section>
<section><h2>Social Security · 2026 Trustees IV.B1</h2><p>All SSA columns are percentages of Social Security taxable payroll, not dollars. OASI and DI are separate trust funds; OASDI is an illustrative combined presentation. Calendar years, intermediate assumptions.</p><div class="twrap"><table><thead><tr><th>Calendar year</th><th>OASI income</th><th>OASI cost</th><th>OASI balance</th><th>DI balance</th><th>OASDI balance</th></tr></thead><tbody>{table_ssa}</tbody></table></div></section>
<section><h2>Actuarial obligations · 2026 Trustees</h2><div class="cards"><div class="card"><small>OASI reserves</small><strong>2032 Q4</strong><small>78% payable on depletion</small></div><div class="card"><small>DI reserves</small><strong>Beyond 2100</strong><small>Separate DI finances</small></div><div class="card"><small>Medicare HI reserves</small><strong>2033 Q2</strong><small>89% payable on depletion</small></div></div><p>Official solvency under a proposed reform cannot be established by adding separately scored options. The 75-year Medicare HI payroll denominator is not the Social Security taxable-payroll denominator.</p></section>
<section><h2>46-source acquisition ledger</h2><p>Filter to inspect confirmed sources and downloaded raw files. Source metadata are not equivalent to data acquisition.</p><input id="q" placeholder="Filter source, agency, or status" aria-label="Filter sources" oninput="filterRows()"><div class="twrap"><table id="sources"><thead><tr><th>Source</th><th>Agency</th><th>Materialization</th><th>Link</th></tr></thead><tbody>{table_catalog}</tbody></table></div></section>
<section class="footer">Primary sources: <a href="https://www.cbo.gov/data/budget-economic-data">CBO budget-economic data</a>, <a href="https://www.ssa.gov/oact/tr/2026/lr4b1.html">SSA 2026 IV.B1</a>, <a href="https://www.ssa.gov/oact/trsum/">SSA/CMS Trustees Summary</a>, <a href="https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html">Census ASEC 2026</a>. The page can be opened offline and does not fetch third-party code.</section></main>
<script>function filterRows(){{const q=document.getElementById('q').value.toLowerCase();for(const row of document.querySelectorAll('#sources tbody tr'))row.hidden=!row.textContent.toLowerCase().includes(q);}}</script></body></html>'''
 from .report_v04 import extend_dashboard
 text=extend_dashboard(text)
 (BASE/'dashboard.html').write_text(text,encoding='utf-8')
