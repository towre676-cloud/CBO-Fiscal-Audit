"""Fetch public machine-readable source files and hash bytes. No estimates computed."""
import argparse, hashlib, json
from pathlib import Path
from urllib.request import urlopen, Request

ROOT=Path(__file__).resolve().parents[1]
BASE='https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/budget/'
FILES={
  'cbo_annual':BASE+'ten_year_budget/annual_fy_2026-02.csv',
  'cbo_revenue':BASE+'revenue_detail/annual_fy_2026-02.csv',
  'cbo_spending':BASE+'spending_detail/annual_fy_2026-02.csv',
  'cbo_trust':BASE+'trust_fund/annual_fy_2026-02.csv',
  'cbo_gdp':'https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/economic/historical_economic/annual_fy_2026-02.csv',
  'cbo_catalog':'https://raw.githubusercontent.com/US-CBO/cbo-data/main/catalog.json',
  'jct_method':'https://www.jct.gov/getattachment/c9ab0cfe-71ce-4912-b0c2-75c9a569ead8/Revenue-Estimating-Process-And-Microeconomic-Research-2026.pdf',
  'cms_2026_tables':'https://www.cms.gov/files/zip/2026-expanded-supplementary-tables-figures.zip',
  'ssa_long_method':'https://www.ssa.gov/oact/TR/2026/2026_LR_Model_Documentation.pdf',
  'ssa_2026_economy':'https://www.ssa.gov/oact/TR/2026/lr6g1.html',
  'ssa_2026_noninterest':'https://www.ssa.gov/oact/TR/2026/lr6g3.html',
  'ssa_2026_reserves':'https://www.ssa.gov/oact/TR/2026/lr6g2.html',
  'ssa_2027_wage_base':'https://www.ssa.gov/news/en/cola/factsheets/2027.html',
  'medpac_2026_exec':'https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_ExecutiveSummary_MedPAC_Report_To_Congress_SEC.pdf',
  'cbo_household_2023_research':'https://www.cbo.gov/system/files/2026-09/62761-additional-data-for-researchers.zip',
  'cbo_household_2023_supp':'https://www.cbo.gov/system/files/2026-09/62761-supp-data.xlsx',
}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--download',nargs='+',choices=sorted(FILES),default=[])
    p.add_argument('--all',action='store_true')
    p.add_argument('--timeout',type=int,default=120)
    a=p.parse_args()
    chosen=list(FILES) if a.all else a.download
    if a.dry_run or not chosen:
        for k,url in FILES.items(): print(f'{k}: {url}')
        if not chosen: return
        if a.dry_run: return
    output=ROOT/'downloads';output.mkdir(exist_ok=True)
    manifest={}
    for k in chosen:
        url=FILES[k]; ext=Path(url.split('?',1)[0]).suffix
        target=output/(k+ext)
        req=Request(url,headers={'User-Agent':'FiscalRazor-public-evidence-research/0.1'})
        try:
            with urlopen(req,timeout=a.timeout) as r:
                if r.status!=200: raise ValueError(f'HTTP {r.status}')
                h=hashlib.sha256();byte_count=0
                with target.open('wb') as f:
                    while True:
                        chunk=r.read(256*1024)
                        if not chunk: break
                        byte_count+=len(chunk)
                        if byte_count>250_000_000: raise ValueError('Source file exceeded 250MB download cap')
                        h.update(chunk);f.write(chunk)
            if not byte_count: raise ValueError('Empty response')
            manifest[k]=dict(url=url,path=str(target.relative_to(ROOT)),sha256=h.hexdigest(),bytes=byte_count,status='downloaded')
            print(f'OK {k} {byte_count} bytes sha256={h.hexdigest()}')
        except Exception as exc:
            target.unlink(missing_ok=True)
            manifest[k]=dict(url=url,status='ERROR',reason=str(exc))
            print(f'ERROR {k}: {exc}')
    (output/'download_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    if any(v['status']=='ERROR' for v in manifest.values()): raise SystemExit(1)

if __name__=='__main__':main()
