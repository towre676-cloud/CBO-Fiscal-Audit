"""FiscalRazor v0.7: validate authentic CBO source bytes; no false policy estimates.

Data provenance:
 CBO US-CBO/cbo-data Feb 2026; public Git blobs.
 Externally supplied metadata cannot be promoted to locally verified raw bytes.
"""
from __future__ import annotations
from decimal import Decimal, getcontext
from collections import defaultdict
import csv, hashlib, io, json
from pathlib import Path

getcontext().prec=30
D=Decimal
ROOT=Path(__file__).resolve().parents[2]
PINFILE=ROOT/'data/v07/cbo_2026_02_git_pins.json'
class SourceGateError(ValueError): pass

def pins():
    return json.loads(PINFILE.read_text(encoding='utf-8'))['files']

def git_blob_sha1(blob:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(blob)).encode('ascii')+b'\x00'+blob).hexdigest()

def parse_csv_bytes(blob:bytes)->list[dict[str,str]]:
    try: text=blob.decode('utf-8-sig')
    except UnicodeError as exc: raise SourceGateError('not UTF-8 CSV') from exc
    if not text or '\x00' in text: raise SourceGateError('non-CSV or empty source')
    rdr=csv.DictReader(io.StringIO(text,newline=''))
    if not rdr.fieldnames or len(set(rdr.fieldnames))!=len(rdr.fieldnames):
        raise SourceGateError('missing or duplicate field names')
    if any(not x for x in rdr.fieldnames): raise SourceGateError('empty field name')
    rows=list(rdr)
    if any(None in row for row in rows): raise SourceGateError('malformed CSV row')
    return rows

def validate_source(original_file:Path,pin:dict)->dict:
    if original_file.is_symlink(): raise SourceGateError('symlink source forbidden')
    if not original_file.is_file(): raise SourceGateError('missing complete raw source')
    payload=original_file.read_bytes()
    actual=git_blob_sha1(payload)
    if actual != pin['git_blob_sha1']: raise SourceGateError('Git blob SHA-1 mismatch')
    rows=parse_csv_bytes(payload)
    if len(rows)!=pin['expected_csv_rows']:
        raise SourceGateError('row count does not match pinned source')
    duplicates=duplicate_keys(rows)
    return {'path':pin['path'],'git_blob_sha1':actual,'sha256':hashlib.sha256(payload).hexdigest(),
            'verified_original_bytes':True,'rows':len(rows),'duplicate_date_variable':sum(len(x)-1 for x in duplicates.values())}

def duplicate_keys(rows:list[dict])->dict[tuple[str,str],list[dict]]:
    bucket=defaultdict(list)
    for row in rows:
        if 'date' not in row or 'variable' not in row: return {}
        bucket[(row['date'],row['variable'])].append(row)
    return {key:items for key,items in bucket.items() if len(items)>1}

def strict_value_pivot(rows:list[dict], *,allow_identical:bool=False)->dict[tuple[str,str],str]:
    """No accidental last-write-wins for trust-fund/long-term economic records."""
    seen={}
    for row in rows:
        if not {'date','variable','value'}<=set(row): raise SourceGateError('need long-format data')
        key=(row['date'],row['variable'])
        if key in seen:
            if not allow_identical or seen[key]!=row['value']:
                raise SourceGateError('duplicate key requires explicit semantic decomposition')
        else:seen[key]=row['value']
    return seen

def six_rank_agi_margins(*,returns_millions:str='180.5',agi_billions:str='26787.8',
                        cumulative_top_shares:dict[str,str]|None=None)->list[dict]:
    """CBO CY2036 projected tax-return AGI rank margins; NOT tax units/households.

    Cumulative shares: top 50 / 25 / 10 / 5 / 1 in percent.
    NB: bottom 50 = 100 - top50, etc.
    """
    if cumulative_top_shares is None:
        cumulative_top_shares={'50':'88.8','25':'70.4','10':'50.0','5':'38.8','1':'23.0'}
    s={k:D(v) for k,v in cumulative_top_shares.items()}
    if set(s)!={'50','25','10','5','1'}:raise SourceGateError('missing cumulative AGI rank shares')
    if not D(100)>=s['50']>=s['25']>=s['10']>=s['5']>=s['1']>=0:
        raise SourceGateError('invalid cumulative percentile distribution')
    groups=[('bottom_50',D('0.50'),D('100')-s['50']),
            ('50_to_75',D('.25'),s['50']-s['25']),
            ('75_to_90',D('.15'),s['25']-s['10']),
            ('90_to_95',D('.05'),s['10']-s['5']),
            ('95_to_99',D('.04'),s['5']-s['1']),
            ('top_1',D('.01'),s['1'])]
    n=D(returns_millions);a=D(agi_billions)
    if n<=0 or a<0:raise SourceGateError('invalid federal rank aggregate')
    if sum((g[1] for g in groups),D(0))!=1 or sum((g[2] for g in groups),D(0))!=100:
        raise SourceGateError('rank shares fail to sum')
    return [{'group':group,'returns_millions':str(n*frac),
             'agi_percent':str(share),'agi_billions':str(a*share/D(100)),
             'average_agi_usd':str((a*share/D(100))/(n*frac)*D(1000))}
            for group,frac,share in groups]

def jensen_top_group_floor(*,top_group_agi_bn:str,top_group_returns_mn:str,
                           per_return_threshold_usd:str,mechanical_rate:str)->dict:
    """For x>=0, sum max(x-T,0) >= max(sum x - N*T,0).
    Source aggregate is tax-return AGI, NOT defined MAGI liability.
    """
    a=D(top_group_agi_bn);n=D(top_group_returns_mn);t=D(per_return_threshold_usd);rate=D(mechanical_rate)
    if a<0 or n<=0 or t<0 or not D(0)<=rate<=1:raise SourceGateError('invalid partial-ID inputs')
    deduction_equiv_bn=n*t/D(1000) # million returns * dollars / 1000 -> billions
    floor=max(D(0),a-deduction_equiv_bn)
    return {'mechanical_lower_base_bn':str(floor),
            'unadjusted_lower_product_bn':str(floor*rate),
            'mechanical_upper_product_bn_nonnegative_agi':str(a*rate),
            'status':'PARTIAL_IDENTIFICATION_NOT_A_POLICY_SCORE',
            'exclusions':'No filing status, MAGI, behavioral response, tax payment timing, returns weights, deductions or cross taxes'}

def verify_2036_budget(r:str,o:str,deficit_signed:str,interest:str,primary_signed:str,gdp:str)->dict:
    R,O,deficit,interest,primary,gdp=map(D,[r,o,deficit_signed,interest,primary_signed,gdp])
    if R-O!=deficit:raise SourceGateError('receipt/outlay sign identity failed')
    if primary-interest!=deficit:raise SourceGateError('primary-interest identity failed')
    if gdp<=0: raise SourceGateError('GDP missing')
    return {'fiscal_year':2036,'gdp_bn':str(gdp),'deficit_signed_bn':str(deficit),
            'gap_to_3pct_bn':str(-deficit-gdp*D('.03')),
            'classification':'EXACT_FROZEN_BASELINE_ARITHMETIC_NOT_REFORM_SCORE'}

def check_spending_accounts(rows:list[dict],official_baseline_outlays_bn:dict[str,str]):
    required={'date','tin','disc_or_mand','category','budget_authority','outlays'}
    if not rows or not required<=set(rows[0]):raise SourceGateError('spending schema mismatch')
    annual=defaultdict(lambda:D('0'))
    for row in rows:
        if not row['tin']: raise SourceGateError('missing Treasury account number')
        annual[row['date']]+=D(row['outlays'])
    for date,official_bn in official_baseline_outlays_bn.items():
        if date not in annual:raise SourceGateError('missing spending fiscal year')
        if abs(annual[date]-D(official_bn)*D(1000))>D('1'):
            raise SourceGateError('spending-account outlays do not reconcile')
    return {'verified_fiscal_years':len(official_baseline_outlays_bn),
            'classification':'SOURCE_AGGREGATE_ACCOUNT_RECONCILIATION_NOT_SPENDING_POLICY_SCORE'}
