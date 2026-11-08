"""FiscalRazor v0.8: public source acquisition, data-class gate and actual-data-only diagnostics.

NO national policy results from synthetic households. 2026 CBO vintage fixed.
"""
from __future__ import annotations
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse
import csv, datetime as dt, hashlib, io, json, math, os, shutil, urllib.request, zipfile
from fiscal_data.v07_calibration import git_blob_sha1, parse_csv_bytes, strict_value_pivot, SourceGateError, check_spending_accounts

ROOT=Path(__file__).resolve().parents[2]
PINS=json.loads((ROOT/'data/v07/cbo_2026_02_git_pins.json').read_text())['files']
D=Decimal
class OriginalSourceError(ValueError):pass
CBO_ALLOWED_DOMAIN='raw.githubusercontent.com'

EXTERNAL_SOURCES={
 'cps_asec_2026_csv':{
 'agency':'Census','unit':'households/families/persons','url':'https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asecpub26csv.zip',
 'kind':'zip','min_bytes':40_000_000,'max_bytes':220_000_000,'catalog_status':'OFFICIAL_DIRECT_URL_CONFIRMED','access_type':'public-use microdata',
 'page':'https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html'},
 'cps_asec_2026_replicates':{
 'agency':'Census','unit':'household/person replicate weights','url':'https://www2.census.gov/programs-surveys/cps/datasets/2026/march/CPS_ASEC_ASCII_REPWGT_2026.ZIP',
 'kind':'zip','min_bytes':20_000_000,'max_bytes':120_000_000,'catalog_status':'OFFICIAL_DIRECT_URL_CONFIRMED','access_type':'public-use microdata',
 'page':'https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html'},
 'cms_medicare_2026_expanded':{
 'agency':'CMS','unit':'CY Medicare actuarial tables','url':'https://www.cms.gov/files/zip/2026-expanded-supplementary-tables-figures.zip',
 'kind':'zip','max_bytes':200_000_000,'catalog_status':'OFFICIAL_DIRECT_URL_CONFIRMED','access_type':'public actuarial supplementary',
 'page':'https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds'},
 'irs_soi_2023_zip_agi':{
 'agency':'IRS','unit':'ZIP-AGI-bin aggregates','url':'https://www.irs.gov/pub/irs-soi/23zpallagi.csv',
 'kind':'csv','min_bytes':100_000,'max_bytes':260_000_000,'catalog_status':'OFFICIAL_DIRECT_URL_CONFIRMED','access_type':'public aggregate, not individual microdata',
 'page':'https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-returns'},
 'irs_soi_2023_state_shares':{
 'agency':'IRS','unit':'state-level aggregates','url':'https://www.irs.gov/pub/irs-soi/23instateshares.csv',
 'kind':'csv','min_bytes':10_000,'max_bytes':100_000_000,'catalog_status':'SOURCE_DOCUMENTED_ENDPOINT_NOT_BYTE_VERIFIED','access_type':'public aggregate',
 'page':'https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-returns'},
 'bls_ce_2024_interview_csv':{
 'agency':'BLS','unit':'2024 consumer-unit interview microdata','url':'https://www.bls.gov/cex/pumd/data/csv/intrvw24.zip',
 'kind':'zip','min_bytes':10_000_000,'max_bytes':100_000_000,
 'catalog_status':'OFFICIAL_2024_CSV_LINK_VERIFIED','access_type':'public-use microdata',
 'page':'https://www.bls.gov/cex/pumd_data.htm'},
 'bls_ce_2024_diary_csv':{
 'agency':'BLS','unit':'2024 consumer-unit diary microdata','url':'https://www.bls.gov/cex/pumd/data/csv/diary24.zip',
 'kind':'zip','min_bytes':1_000_000,'max_bytes':50_000_000,
 'catalog_status':'OFFICIAL_2024_CSV_LINK_VERIFIED','access_type':'public-use microdata',
 'page':'https://www.bls.gov/cex/pumd_data.htm'},
 'bls_ce_2025_interview_csv':{
 'agency':'BLS','unit':'2025 consumer-unit interview microdata',
 'url':'https://www.bls.gov/cex/pumd/data/csv/intrvw25.zip',
 'kind':'zip','min_bytes':10_000_000,'max_bytes':100_000_000,
 'catalog_status':'OFFICIAL_2025_ARCHIVE_ENDPOINT_RESPONDED_ZIP_BYTES_NOT_FETCHED',
 'access_type':'public-use microdata, requires 2025 noncollection-month treatment',
 'page':'https://www.bls.gov/cex/pumd_data.htm'},
 'bls_ce_2025_diary_csv':{
 'agency':'BLS','unit':'consumer units','url':None,'kind':'zip','min_bytes':400_000,'max_bytes':80_000_000,
 'catalog_status':'LANDING_PAGE_VERIFIED_DIRECT_HREF_NOT_RESOLVED','access_type':'public-use microdata',
 'page':'https://www.bls.gov/cex/pumd_data.htm'},
}


def source_specs():
 return {('cbo_'+str(i).zfill(2)):{'agency':'CBO','unit':'varies; see accompanying schema',
 'url':p['source_url'],'kind':'csv','expected_git_blob_sha1':p['git_blob_sha1'],
 'expected_csv_rows':p['expected_csv_rows'],'path':p['path'],'max_bytes':25_000_000,
 'catalog_status':'OFFICIAL_REPOSITORY_GIT_SHA_CONFIRMED','access_type':'public aggregate',
 'page':'https://github.com/US-CBO/cbo-data'}
  for i,p in enumerate(PINS,1)} | EXTERNAL_SOURCES


def checked_spec(name,spec):
 url=spec.get('url')
 if not url:raise OriginalSourceError('DIRECT_URL_UNRESOLVED')
 parsed=urlparse(url)
 if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password:
  raise OriginalSourceError('ONLY_PUBLIC_HTTPS_ALLOWED')
 if name.startswith('cbo_') and parsed.hostname!=CBO_ALLOWED_DOMAIN:
  raise OriginalSourceError('CBO_HOST_MISMATCH')
 if '..' in parsed.path.split('/') or parsed.path.endswith('/'):
  raise OriginalSourceError('SOURCE_PATH_UNSAFE')
 return parsed


def verify_payload(payload:bytes,spec:dict):
 if spec.get('max_bytes') is not None and len(payload)>spec['max_bytes']:
  raise OriginalSourceError('LOCAL_ORIGINAL_EXCEEDS_APPROVED_SIZE_LIMIT')
 if not payload:raise OriginalSourceError('EMPTY_SOURCE_FILE')
 if spec.get('min_bytes') is not None and len(payload)<spec['min_bytes']:
  raise OriginalSourceError('SOURCE_TOO_SMALL_FOR_VERIFIED_DISTRIBUTION')
 kind=spec['kind'];b=payload.lstrip()[:250].lower()
 if b.startswith((b'<!doctype html',b'<html',b'<?xml')):raise OriginalSourceError('HTML_OR_XML_NOT_DATA')
 if kind=='zip':
  if not payload.startswith(b'PK\x03\x04'):raise OriginalSourceError('BAD_ZIP_MAGIC')
  try:
   with zipfile.ZipFile(io.BytesIO(payload)) as z:
    infos=z.infolist()
    if not infos or len(infos)>5000:raise OriginalSourceError('UNEXPECTED_ARCHIVE_ENTRY_COUNT')
    if sum(i.file_size for i in infos)>5_000_000_000:raise OriginalSourceError('ZIP_EXPANDED_TOO_LARGE')
    for entry in infos:
     p=Path(entry.filename.replace('\\','/'))
     if p.is_absolute() or '..' in p.parts or entry.file_size>1_500_000_000:
      raise OriginalSourceError('UNSAFE_ZIP_MEMBER')
    bad=z.testzip()
    if bad:raise OriginalSourceError('ZIP_CRC_FAILURE '+bad)
  except zipfile.BadZipFile as e:raise OriginalSourceError('CORRUPT_ZIP') from e
 if kind=='csv':
  try: text=payload.decode('utf-8-sig')
  except UnicodeError as e:raise OriginalSourceError('NOT_UTF8_CSV') from e
  if '\x00' in text:raise OriginalSourceError('NUL_IN_CSV')
  reader=csv.reader(io.StringIO(text,newline=''))
  head=next(reader,None)
  if head is None or len(set(head))!=len(head) or len(head)<3:raise OriginalSourceError('BAD_CSV_HEADER')
  count=0
  for row in reader:
   if len(row)!=len(head):raise OriginalSourceError('MALFORMED_CSV_ROW')
   count+=1
  if count==0:raise OriginalSourceError('CSV_HAS_NO_RECORDS')
  if spec.get('expected_csv_rows') is not None and count!=spec['expected_csv_rows']:
   raise OriginalSourceError('ROW_COUNT_MISMATCH')
 if spec.get('expected_git_blob_sha1') and git_blob_sha1(payload)!=spec['expected_git_blob_sha1']:
  raise OriginalSourceError('GIT_BLOB_SHA1_MISMATCH')
 return {'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload),
         'git_blob_sha1':git_blob_sha1(payload) if spec.get('expected_git_blob_sha1') else None,
         'integrity_verified':True,'cryptographic_publisher_pin_matched':bool(spec.get('expected_git_blob_sha1'))}


def destination(root,name,spec):
 root=Path(root).resolve()
 ext='.zip' if spec['kind']=='zip' else '.csv'
 return root / (name+ext)


def download_source(name,root,*,max_bytes_override=None):
 specs=source_specs()
 if name not in specs:raise OriginalSourceError('UNKNOWN_SOURCE')
 spec=specs[name];checked_spec(name,spec)
 dest=destination(root,name,spec)
 maxb=max_bytes_override if max_bytes_override is not None else spec['max_bytes']
 if not (1<=maxb<=6_000_000_000):raise OriginalSourceError('INVALID_FILE_LIMIT')
 dest.parent.mkdir(parents=True,exist_ok=True)
 tmp=dest.with_suffix(dest.suffix+'.pending')
 if tmp.exists():tmp.unlink()
 try:
  request=urllib.request.Request(spec['url'],headers={
   'User-Agent':'FiscalRazor/0.8 (+open public-data academic reproducibility; no private records)',
   'Accept':'application/octet-stream, text/csv, */*'})
  with urllib.request.urlopen(request,timeout=60) as resp,open(tmp,'wb') as f:
   final_url=resp.geturl()
   final_host=urlparse(final_url).hostname or ''
   if not (final_url.startswith('https://') and
      (final_host==urlparse(spec['url']).hostname or final_host.endswith('.gov'))):
    raise OriginalSourceError('UNVERIFIED_DOWNLOAD_REDIRECT_HOST')
   declared=resp.headers.get('Content-Length')
   if declared and int(declared)>maxb:raise OriginalSourceError('REMOTE_FILE_SIZE_EXCEEDS_LIMIT')
   total=0
   while True:
    chunk=resp.read(1<<20)
    if not chunk:break
    total+=len(chunk)
    if total>maxb:raise OriginalSourceError('DOWNLOADED_FILE_EXCEEDS_LIMIT')
    f.write(chunk)
  payload=tmp.read_bytes();receipt=verify_payload(payload,spec)
  original_receipt={'id':name,'source_url':spec['url'],'final_url':final_url,
   'sha256':receipt['sha256'],'bytes':receipt['bytes'],
   'official_git_sha1':spec.get('expected_git_blob_sha1'),
   'download_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
   'authentication':'HTTPS_ORIGIN_RECEIPT_NOT_PUBLISHER_SIGNED',
   'data_class':spec['access_type']}
  # Both source file and receipt are constructed only after complete transfer and validation.
  tmp.replace(dest)
  receiptpath=dest.with_suffix(dest.suffix+'.origin.json')
  tmpr=receiptpath.with_suffix(receiptpath.suffix+'.pending')
  tmpr.write_text(json.dumps(original_receipt,sort_keys=True,indent=2)+'\n')
  tmpr.replace(receiptpath)
  return {'id':name,'local_file':str(dest),'source_url':spec['url'],**receipt,
          'provenance_class':('GIT_BLOB_PINNED' if spec.get('expected_git_blob_sha1')
           else 'CAPTURED_FROM_VERIFIED_HTTPS_ORIGIN_NOT_PUBLISHER_CHECKSUM_SIGNED'),
          'verified_at':original_receipt['download_utc'], 'source_class':spec['access_type']}
 finally:
  if tmp.exists():tmp.unlink()


def verify_local(name,root):
 spec=source_specs().get(name)
 if spec is None:raise OriginalSourceError('UNKNOWN_SOURCE')
 path=destination(root,name,spec)
 if path.is_symlink():raise OriginalSourceError('SYMLINK_AS_ORIGINAL_SOURCE_FORBIDDEN')
 if not path.is_file():raise OriginalSourceError('ORIGINAL_BYTES_NOT_ACQUIRED')
 checked_spec(name,spec)
 receipt=verify_payload(path.read_bytes(),spec)
 if spec.get('expected_git_blob_sha1'):
  prov='GIT_BLOB_PINNED'
 else:
  rp=path.with_suffix(path.suffix+'.origin.json')
  if not rp.is_file():raise OriginalSourceError('UNPINNED_ORIGINAL_PROVENANCE_RECEIPT_MISSING')
  try:record=json.loads(rp.read_text())
  except (ValueError,UnicodeError) as e:raise OriginalSourceError('BAD_ORIGIN_PROVENANCE_RECEIPT') from e
  if any([record.get('id')!=name,record.get('source_url')!=spec['url'],
   record.get('sha256')!=receipt['sha256'],record.get('bytes')!=receipt['bytes'],
   record.get('authentication')!='HTTPS_ORIGIN_RECEIPT_NOT_PUBLISHER_SIGNED']):
   raise OriginalSourceError('ORIGIN_PROVENANCE_MISMATCH')
  prov='CAPTURED_FROM_VERIFIED_HTTPS_ORIGIN_NOT_PUBLISHER_CHECKSUM_SIGNED'
 return {'id':name,'local_file':str(path),'source_url':spec['url'],
         **receipt,'provenance_class':prov,'source_class':spec['access_type']}


def status(root):
 allsp=source_specs()
 out=[]
 for key,spec in allsp.items():
  try:
   r=verify_local(key,root)
   state='VERIFIED_ORIGINAL_LOCAL';sha=r['sha256'];n=r['bytes']
  except OriginalSourceError as e:
   source_path=destination(root,key,spec)
   state=('LOCAL_BYTES_UNVERIFIED' if source_path.exists() else
          'NOT_ACQUIRED' if spec.get('url') else 'DIRECT_LINK_UNRESOLVED')
   sha=None;n=source_path.stat().st_size if source_path.exists() else 0
  out.append({'id':key,'agency':spec['agency'],'state':state,'bytes':n,'sha256':sha,
              'url':spec.get('url'),'landing_page':spec['page'],'source_class':spec['access_type']})
 return out


def final_outlay_checks(ten_year_rows:list[dict],spending_rows:list[dict]):
 """Full CBO account-level FY2026–2036: outlay reconciliation, BA != cash.
 No duplicate pivots. All 11 official FY aggregate totals required.
 """
 bykey={(r['date'],r['variable']):D(r['value']) for r in ten_year_rows
        if 'variable' in r and r['variable']=='proj_outlays_total'}
 expected={f'FY{y}':bykey[(f'FY{y}','proj_outlays_total')] for y in range(2026,2037)}
 report=check_spending_accounts(spending_rows,{y:str(v) for y,v in expected.items()})
 seen=defaultdict(set)
 cat=defaultdict(lambda:defaultdict(D))
 for r in spending_rows:
  y=r['date'];tin=r['tin'];seen[y].add(tin)
  cat[y][r['category']]+=D(r['outlays'])
  if r['disc_or_mand']=='Discretionary' and r['category']=='Defense':
   cat[y]['_defense_budget_authority']+=D(r['budget_authority'])
  if r['disc_or_mand']=='Discretionary' and r['category']=='Defense':
   cat[y]['_defense_outlays']+=D(r['outlays'])
 for y in expected:
  if len(seen[y])!=1712:raise OriginalSourceError('CBO_TIN_UNIVERSE_MISMATCH')
  if abs(cat[y]['_defense_outlays']/1000-D(next(r['value'] for r in ten_year_rows
                    if r.get('date')==y and r.get('variable')=='proj_disc_defense')))>D('.001'):
   raise OriginalSourceError('DEFENSE_OUTLAY_SUBTOTAL_MISMATCH')
 return {'years':11,'spending_records':len(spending_rows),'unique_account_ids':len(set().union(*seen.values())),
         'report':report,'FY2036_defense_outlays_bn':str(cat['FY2036']['_defense_outlays']/1000),
         'FY2036_defense_budget_authority_bn':str(cat['FY2036']['_defense_budget_authority']/1000),
         'classification':'ORIGINAL_ACCOUNT_RECONCILIATION_NOT_POLICY_SAVINGS'}


def weighted_household_income_2026(cps_zip:Path,house_member:str,*,weight_scale:D=D(100)):
 """Observed 2026 ASEC household incomes only; not tax returns, CE units, or VAT incidence.
 All 88,026 ASEC household records must be present; income estimates use only
 interviewed households (53,321 in published 2026 CPS ASEC). Actual records only.
 """
 from fiscal_data.cps_preflight import inspect_archive, CPSDataError
 if not Path(cps_zip).is_file():raise OriginalSourceError('CPS_ORIGINAL_NOT_MATERIALIZED')
 if weight_scale!=100:raise OriginalSourceError('CPS_2026_HSUP_WGT_TWO_IMPLIED_DECIMALS')
 out=defaultdict(lambda: {'sample_n':0,'weight':D(0),'weighted_income':D(0)})
 with zipfile.ZipFile(cps_zip) as z:
  if house_member not in z.namelist():raise OriginalSourceError('HOUSEHOLD_MEMBER_NOT_FOUND')
  with z.open(house_member) as f:
   rr=csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig',newline=''))
   needed={'H_IDNUM','HSUP_WGT','HTOTVAL','HPCTCUT','H_HHTYPE'}
   if not needed<=set(rr.fieldnames or []):raise OriginalSourceError('CPS_2026_HH_REQUIRED_FIELDS_MISSING')
   seen=set();n=0;interviewed=0
   for r in rr:
    n+=1
    if r['H_HHTYPE']!='1':continue # noninterview not in weighted population
    interviewed+=1
    key=r['H_IDNUM']
    if key in seen:raise OriginalSourceError('CPS_DUPLICATE_HOUSEHOLD_ID')
    seen.add(key)
    w=D(r['HSUP_WGT'])/weight_scale
    inc=D(r['HTOTVAL'])
    if not (w.is_finite() and w>0 and inc.is_finite()):raise OriginalSourceError('INVALID_INCOME_OR_WEIGHT')
    group=int(r['HPCTCUT'])
    if not 1<=group<=20:raise OriginalSourceError('PERCENTILE_INVALID_OR_NIU')
    o=out[group];o['sample_n']+=1;o['weight']+=w;o['weighted_income']+=w*inc
 if n!=88026:raise OriginalSourceError('CPS_2026_HOUSEHOLD_RECORD_COUNT_MISMATCH')
 if interviewed!=53321:raise OriginalSourceError('CPS_2026_INTERVIEWED_HOUSEHOLD_COUNT_MISMATCH')
 tot=sum((v['weight'] for v in out.values()),D(0))
 if not D('100000000')<tot<D('170000000') or len(out)!=20:
  raise OriginalSourceError('CPS_HOUSEHOLD_UNIVERSE_OR_QUINTILE_INCOMPLETE')
 return {'original_source_sha256':hashlib.sha256(Path(cps_zip).read_bytes()).hexdigest(),
  'all_household_records':n,'interviewed_household_records':interviewed,'weighted_interviewed_households':str(tot),
  'by_income_5pct':[{'group':k,'sample_n':v['sample_n'],'weighted_households':str(v['weight']),
            'weighted_income_total_usd':str(v['weighted_income'])} for k,v in sorted(out.items())],
  'classification':'ACTUAL_PUBLIC_USE_HOUSEHOLD_INCOME_DISTRIBUTION_NOT_REFORM_INCIDENCE'}


def soi_2023_aggregate_checks(csv_path):
 """IRS ZIP AGI-bin public aggregates, not a record-level tax sample."""
 p=Path(csv_path)
 if not p.is_file():raise OriginalSourceError('IRS_AGGREGATE_SOURCE_MISSING')
 with p.open('r',encoding='utf-8-sig',newline='') as f:
  rr=csv.DictReader(f)
  expected={'STATE','ZIPCODE','AGI_STUB','N1','A00100'}
  if not expected<=set(rr.fieldnames or []):raise OriginalSourceError('IRS_SOI_SCHEMA_MISMATCH')
  cells=0;by_state=defaultdict(lambda:[0,D(0)])
  for row in rr:
   if row['ZIPCODE'] in ('00000',0,'0'):continue # county/state aggregation rows excluded
   n=D(row['N1']);agi=D(row['A00100'])
   if n<0 or not n.is_finite() or not agi.is_finite():raise OriginalSourceError('SOI_BAD_AGGREGATE_CELL')
   cells+=1;by_state[row['STATE']][0]+=1;by_state[row['STATE']][1]+=n
 if cells<1000:raise OriginalSourceError('IRS_SOI_AGGREGATE_INCOMPLETE')
 return {'aggregate_zip_agi_rows':cells,'state_groups':len(by_state),
         'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
         'classification':'REAL_IRS_AGGREGATES_NOT_INDIVIDUAL_TAX_UNITS_OR_SCORES'}
