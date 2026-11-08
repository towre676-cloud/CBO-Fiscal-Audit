"""Offline Medicare section. Published annual data, explicitly non-scoring slider."""
import json,html
from decimal import Decimal
from .medicare_cash import validate_hi,validate_smi,uniform_incremental_hi_inflow_floor,BASE

def extend_dashboard(text):
    hi=validate_hi();smi=validate_smi()
    yearly=[]
    for i,row in enumerate(hi):
        y=row['calendar_year']
        gross=row['expenditures_bn']+smi['SMI'][i]['expenditures_bn']
        yearly.append({'year':y,'assets':float(row['assets_year_end_bn']),
                       'hi_exp':float(row['expenditures_bn']), 'gross_exp':float(gross)})
    table=''.join(f'<tr><td>{r["year"]}</td><td>{r["hi_exp"]:,.1f}</td><td>{r["gross_exp"]-r["hi_exp"]:,.1f}</td><td>{r["gross_exp"]:,.1f}</td><td>{r["assets"]:,.1f}</td></tr>' for r in yearly)
    f=uniform_incremental_hi_inflow_floor()
    floor=f['annual_increment_bn']
    # Embed only data originating in already-verified local source tables.
    dataset=json.dumps(yearly,separators=(',',':'))
    addon=f'''<section id="medicare-dataset">
<h2>Medicare · CMS 2026 actuarial tables</h2>
<p>Trustees' <a href="https://www.cms.gov/oact/tr/2026">official Table II.E1</a> and <a href="https://www.cms.gov/oact/tr/2026">Table II.F1</a> under intermediate assumptions, calendar years. These are <strong>gross trust-fund outlays</strong>, not CBO unified-budget net Medicare outlays.</p>
<div class="cards"><div class="card"><small>2025 gross Medicare trust-fund expenditures</small><strong>$1,210.0B</strong><small>2025 actual experience, HI + SMI</small></div>
<div class="card"><small>2035 gross Medicare trust-fund expenditures</small><strong>$2,543.1B</strong><small>Trustees' projection, HI + SMI</small></div>
<div class="card"><small>2035 hypothetical HI balance after baseline depletion</small><strong>−$296.5B</strong><small>Not legally borrowable HI reserves</small></div></div>
<div class="note"><strong>Test a fixed-baseline financing floor, not a reform forecast.</strong> The interactive amount is uniform *additional annual HI income* beginning CY2027, no changes in economic conditions, medical costs, interest, or provider payments. It cannot establish quarterly liquidity or 75-year solvency.</div>
<div class="card"><label for="hi-topup">Additional yearly HI income (2027–2035): <strong id="hi-q">$0 billion</strong></label>
<input aria-label="Additional annual HI receipts in billions" style="width:100%;accent-color:#165b87" id="hi-topup" type="range" min="0" max="150" step="0.25" value="0" oninput="updateHI()">
<div style="display:flex;gap:12px;flex-wrap:wrap;color:var(--muted);font-size:13px"><span>Minimum to make CY2035 year-end reserve nonnegative: <strong>${float(floor):,.2f}B/year</strong></span><span>Minimum to meet 100% reserve ratio at beginning of CY2035 (not all years): <strong>$130.73B/year</strong></span></div>
<svg role="img" aria-label="HI year-end reserves in billions 2025 to 2035, source baseline versus illustrative fixed contribution" id="hi-svg" viewBox="0 0 900 320" style="width:100%;max-width:900px;height:auto;background:#fbfcfc" xmlns="http://www.w3.org/2000/svg"></svg>
<p id="hi-interpretation" class="footer" aria-live="polite"></p></div>
<div class="twrap"><table><thead><tr><th>Calendar year</th><th>HI gross outlays ($B)</th><th>SMI gross outlays ($B)</th><th>Total gross outlays ($B)</th><th>HI year-end assets ($B)</th></tr></thead><tbody>{table}</tbody></table></div>
<p class="footer">2033–2035 HI asset balances represent hypothetical continued scheduled benefits after the predicted 2033 Q2 depletion. CMS and CBO use different periods and net-versus-gross accounts; direct addition or substitution is not valid.</p>
</section>'''
    heading='<section><h2>46-source acquisition ledger</h2>'
    if heading not in text:raise ValueError('DASHBOARD_INSERTION_MARKER_CHANGED')
    count=text.count('<tr><td>cbo_budget_10yr</td>')
    if count!=1:raise ValueError('DASHBOARD_BASELINE_EXPECTED')
    text=text.replace(heading,addon+'\n<section><h2>51-source acquisition ledger</h2>')
    text=text.replace('FiscalRazor Data Foundation','FiscalRazor v0.4 · Medicare Cashflow Lab')
    text=text.replace('Source-grounded federal data · 2026-11-06','Source-grounded federal data · v0.4.0 · 2026-11-06')
    text=text.replace('function filterRows(){','''const cmsHiData=\x20'''+dataset+''';
function updateHI(){
 const svg=document.getElementById('hi-svg');const q=Number(document.getElementById('hi-topup').value);
 document.getElementById('hi-q').textContent='$'+q.toFixed(2)+' billion';
 const base=cmsHiData.map(z=>({x:z.year,y:z.assets}));
 const altered=cmsHiData.map(z=>({x:z.year,y:z.assets+Math.max(0,z.year-2026)*q}));
 const vals=base.concat(altered).map(z=>z.y);const lo=Math.floor((Math.min(...vals)-40)/100)*100,hi=Math.ceil((Math.max(...vals)+40)/100)*100;
 const X=x=>70+(x-2025)*77;const Y=y=>260-(y-lo)/(hi-lo)*210;
 const fmt=arr=>arr.map(p=>X(p.x)+','+Y(p.y)).join(' ');
 const ref=0>=lo && 0<=hi?'<line x1="70" x2="840" y1="'+Y(0)+'" y2="'+Y(0)+'" stroke="#a0b0b5" stroke-dasharray="5 4"/>':'';
 let t='<rect x="0" y="0" width="900" height="320" fill="white"/>'+ref;
 for(let i=0;i<5;i++){const value=lo+(hi-lo)*i/4;t+='<text x="60" y="'+(Y(value)+4)+'" font-size="12" text-anchor="end" fill="#667985">'+value.toFixed(0)+'</text>';}
 [2025,2027,2029,2031,2033,2035].forEach(y=>t+='<text x="'+X(y)+'" y="282" text-anchor="middle" font-size="13" fill="#536d79">'+y+'</text>');
 t+='<polyline points="'+fmt(base)+'" stroke="#b8723b" stroke-width="3" fill="none"/>';
 t+='<polyline points="'+fmt(altered)+'" stroke="#165b87" stroke-width="3" fill="none"/>';
 t+='<text x="70" y="18" font-size="14" fill="#b8723b">CMS baseline</text><text x="250" y="18" font-size="14" fill="#165b87">Fixed-payment calculation (NOT an official score)</text>';
 svg.innerHTML=t;
 const final=altered[altered.length-1].y;
 document.getElementById('hi-interpretation').textContent='CY2035 hypothetical year-end HI reserves with additional fixed inflow: $'+final.toFixed(2)+'B. Source and assumptions unchanged; not a forecast of effects under legislation.';
}
updateHI();
function filterRows(){''')
    return text
