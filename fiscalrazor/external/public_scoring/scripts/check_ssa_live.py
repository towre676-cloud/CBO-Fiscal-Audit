"""Fetch official SSA 2026 trustees HTML pages and cross-check curated rows.

A LIVE independent comparison when executed with network access. Unlike unit
checks of included transcriptions this tool checks the current downloaded
original HTML, records its exact SHA-256 and FAILS on source/layout changes.
Requires: beautifulsoup4 (pip install beautifulsoup4).
"""
from __future__ import annotations
from pathlib import Path
import csv, re, hashlib, json, urllib.request, argparse
from decimal import Decimal as D, InvalidOperation
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
JOBS=[
 ('ssa_economy','https://www.ssa.gov/oact/TR/2026/lr6g1.html','ssa_trustees_2026_economic_cy.csv',
  ['oasdi_taxable_payroll_billion','nominal_gdp_billion']),
 ('ssa_flows','https://www.ssa.gov/oact/TR/2026/lr6g3.html','ssa_trustees_2026_oasdi_noninterest_cy.csv',
  ['oasi_noninterest_income_billion','oasi_cost_billion','oasi_noninterest_balance_billion',
   'di_noninterest_income_billion','di_cost_billion','di_noninterest_balance_billion',
   'oasdi_noninterest_income_billion','oasdi_cost_billion','oasdi_noninterest_balance_billion']),
 ('ssa_reserves','https://www.ssa.gov/oact/TR/2026/lr6g2.html','ssa_trustees_2026_oasdi_reserves_cy.csv',
  ['noninterest_income_billion','interest_income_billion','total_income_billion',
   'cost_billion','end_reserves_billion']),
]

def normal_number(s):
    s=s.strip().replace(',','').replace('−','-').replace('–','-').replace('$','').replace('%','')
    s=re.sub(r'\s+', '',s)
    try:return D(s)
    except (InvalidOperation,ValueError):return None


def match_source_html(content, filename, columns):
    soup=BeautifulSoup(content,'html.parser')
    by_year={}
    for tr in soup.find_all('tr'):
        cells=tr.find_all(['td','th'],recursive=False)
        if len(cells)<2: continue
        first=cells[0].get_text(' ',strip=True)
        m=re.match(r'^\s*(20[2-9]\d)(?:\b|\s|$)',first)
        if not m:continue
        y=int(m.group(1))
        if y in by_year:continue # first projected intermediate series precedes low/high cost
        nums=[]
        for c in cells[1:]:
            v=normal_number(c.get_text(' ',strip=True))
            if v is not None:nums.append(v)
        if nums:by_year[y]=nums
    with (ROOT/'data'/filename).open(newline='') as f:records=list(csv.DictReader(f))
    failures=[]
    for r in records:
        y=int(r['calendar_year'])
        if y not in by_year:
            failures.append(f'{filename} CY{y} missing in parsed first-projection rows')
            continue
        expected=[D(r[c]) for c in columns]
        got=by_year[y]
        # Values should form an in-order subsequence, because source HTML can
        # contain spacer cells and the table may expose extra metadata columns.
        idx=0
        for n in got:
            if idx<len(expected) and n==expected[idx]: idx+=1
        if idx!=len(expected): failures.append(f'{filename} CY{y} expected {expected}, fetched numeric sequence {got}')
    return failures


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--timeout',type=int,default=60)
    p.add_argument('--output',default=str(ROOT/'downloads'/'ssa_html_verification'))
    a=p.parse_args()
    dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    result={}
    for name,url,file,cols in JOBS:
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'FiscalRazor-Independent-Public-Source-Check/1.0'})
            with urllib.request.urlopen(req,timeout=a.timeout) as res:
                if res.status!=200:raise RuntimeError(f'HTTP {res.status}')
                content=res.read(5_000_000)
            sha=hashlib.sha256(content).hexdigest()
            (dest/(name+'.html')).write_bytes(content)
            issues=match_source_html(content,file,cols)
            result[name]={'url':url,'sha256':sha,'bytes':len(content),'verified':not issues,'issues':issues,'local_file':file}
        except Exception as exc:
            result[name]={'url':url,'verified':False,'issues':[str(exc)],'local_file':file}
    (dest/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if any(not x['verified'] for x in result.values()):raise SystemExit(1)

if __name__=='__main__':main()
