from pathlib import Path
import sys,csv,json,itertools
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.v06_law import EXPECTED_IDS,policies
from fiscal_data.v06_frontier import PAIRS
DST=ROOT/'data/v06'

def csvwrite(filename,fields,rows):
 with (DST/filename).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

p=policies()
pr=[]
for fy in range(2027,2037):
 for id in EXPECTED_IDS:
  pr.append({'fy':fy,'provision':id,'score_lead':p[id]['score_lead'],
  'primary_balance_effect_bn':'','federal_receipts_delta_bn':'','noninterest_outlays_delta_bn':'',
  'OASI_cash_bn':'','DI_cash_bn':'','HI_cash_bn':'','SMI_B_cash_bn':'','SMI_D_cash_bn':'',
  'source_url':'','source_sha256':'','fiscalization_method':'','status':'UNSCORED_NOT_ZERO'})
csvwrite('provision_year_120_UNSCORED_TEMPLATE.csv',list(pr[0]),pr)
introws=[{'fy':y,'a':a,'b':b,'net_primary_balance_effect_bn':'','source_url':'','source_sha256':'','model_method':'','status':'INTERACTION_NOT_SCORED_NOT_ZERO'} for y in range(2027,2037) for a,b in PAIRS]
csvwrite('interaction_year_90_UNSCORED_TEMPLATE.csv',list(introws[0]),introws)
allpairs=[{'a':a,'b':b,'priority':'DESIGNATED_CORE' if (a,b) in PAIRS or (b,a) in PAIRS else 'UNSCORED_POSSIBLE','zero_assumption':'NOT_PERMITTED'} for a,b in itertools.combinations(EXPECTED_IDS,2)]
csvwrite('all_policy_pairs_66.csv',list(allpairs[0]),allpairs)
print(json.dumps({'provision_years':len(pr),'designated_interaction_years':len(introws),'total_unordered_pairs':len(allpairs)},indent=2))
