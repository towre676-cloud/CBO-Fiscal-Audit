"""Scientific admission tests for a combined federal reform proposal."""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
REQUIRED=('legislative_text','effective_dates','current_law_cutoff','official_cbo_combined_score','official_jct_combined_score',
          'ssa_oasi_di_joint_actuarial_score','cms_hi_joint_actuarial_score','household_microdata_distribution','independent_reconciliation')

@dataclass(frozen=True)
class Gate:
    criterion:str
    status:str
    explanation:str

def assess(metadata):
    results=[]
    for key in REQUIRED:
        x=metadata.get(key)
        if not isinstance(x,dict) or x.get('status')!='VERIFIED' or not x.get('source_url') or not x.get('source_date'):
            results.append(Gate(key,'BLOCKED','Requires dated evidence, exact text and reproducible record; placeholder rejected'))
        else:
            results.append(Gate(key,'PENDING_MANUAL_AUDIT','Provenance fields present; substantive proof not yet independently assessed'))
    return results

def release_combined_score(metadata):
    gates=assess(metadata)
    if any(x.status!='VERIFIED' for x in gates):
        raise ValueError('NO_OFFICIAL_COMBINED_SCORE: '+', '.join(x.criterion for x in gates))
    raise AssertionError('Any change to this fail-closed admission policy requires separately audited implementation')
