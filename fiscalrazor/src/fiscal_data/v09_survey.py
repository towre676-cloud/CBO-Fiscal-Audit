"""Source-neutral rigorous survey estimators; only produce national labels with real admitted data.

CPS ASEC: full sample and exactly 160 replication weights, 4/160 variance multiplier.
Input records are already harmonized household records from a genuine, independently
verified Census original; do not silently join Census/IRS/BLS populations or synthesize.
"""
from __future__ import annotations
from decimal import Decimal as D

class SurveyEvidenceError(ValueError):
    pass

REPLICATES=160

def _num(v):
    try: d=D(str(v))
    except (ValueError,ArithmeticError,TypeError): raise SurveyEvidenceError('NOT_NUMERIC')
    if not d.is_finite(): raise SurveyEvidenceError('NONFINITE_SURVEY_VALUE')
    return d

def replicate_standard_error(point,replicates):
    """Census successive-difference replicate variance: 4/160 * sum((rep-point)^2)."""
    if len(replicates)!=REPLICATES:raise SurveyEvidenceError('REQUIRES_160_REPLICATE_ESTIMATES')
    p=_num(point);r=[_num(x) for x in replicates]
    variance=D(4)/D(REPLICATES)*sum(((x-p)**2 for x in r),D(0))
    return {'point':p,'variance':variance,'standard_error':variance.sqrt(),
            'method':'CENSUS_ASEC_160_SDR_REPLICATES','assumption':'FAY_0.5_4_OVER_160'}

def weighted_mean_with_replicates(records, *,value_field,full_weight_field,replicate_fields,
                                  weight_scale='1',min_records=2,origin_receipt=None):
    """Recompute point/replicate weighted means. No source-name guessing.

    origin_receipt must be a validated original-source receipt. This guards only
    output classification; no caller-supplied string is treated as authenticity proof.
    """
    if len(replicate_fields)!=REPLICATES or len(set(replicate_fields))!=REPLICATES:
        raise SurveyEvidenceError('MUST_MAP_160_DISTINCT_DOCUMENTED_WEIGHT_COLUMNS')
    scale=_num(weight_scale)
    if scale<=0:raise SurveyEvidenceError('INVALID_WEIGHT_SCALE')
    vals=[];wt=[];rw=[]
    needed={value_field,full_weight_field,*replicate_fields}
    for rec in records:
        if not needed<=rec.keys():raise SurveyEvidenceError('SOURCE_RECORD_MISSING_DOCUMENTED_FIELDS')
        x=_num(rec[value_field]);w=_num(rec[full_weight_field])/scale
        r=[_num(rec[c])/scale for c in replicate_fields]
        if w<0 or any(i<0 for i in r):raise SurveyEvidenceError('NEGATIVE_SURVEY_WEIGHT')
        vals.append(x);wt.append(w);rw.append(r)
    if len(vals)<min_records:raise SurveyEvidenceError('TOO_FEW_SOURCE_RECORDS')
    denom=sum(wt,D(0))
    if denom<=0:raise SurveyEvidenceError('ZERO_FULL_SAMPLE_WEIGHT')
    point=sum((x*w for x,w in zip(vals,wt)),D(0))/denom
    estimates=[]
    for j in range(REPLICATES):
        dj=sum((w[j] for w in rw),D(0))
        if dj<=0:raise SurveyEvidenceError('ZERO_REPLICATE_DENOMINATOR')
        estimates.append(sum((x*w[j] for x,w in zip(vals,rw)),D(0))/dj)
    se=replicate_standard_error(point,estimates)
    return {'estimate':str(point),'standard_error':str(se['standard_error']),
            'variance':str(se['variance']),'n_source_records':len(vals),
            'full_sample_weight_total':str(denom),'replicate_estimates':list(map(str,estimates)),
            'origin_status':'PROVENANCE_NOT_ESTABLISHED_FOR_SYNTHETIC_FIXTURES'
                if origin_receipt is None else 'CALLER_CLAIMS_VERIFIED_ORIGIN_REQUIRES_EXTERNAL_REPLAY',
            'estimator':'FULL_SAMPLE_SURVEY_WEIGHTED_MEAN_WITH_160_SDR_REPLICATES'}

REQUIRED_HOUSEHOLD_INCIDENTS=('household_group','base_disposable_income','taxable_consumption',
     'vat_credit','survey_weight','source_linkage_receipt')

def conditional_vat_incidence(records, *,rate,full_source_gate=False):
    """Compute conditional mechanical burdens on supplied records.

    full_source_gate is NOT a cryptographic proof and output is NEVER labeled
    national: actual survey linkage, calibration, replicate variance and source
    receipts must be independently verified in a separate admission workflow.
    """
    r=_num(rate)
    if not r.is_finite() or not D(0)<=r<=D(1):raise SurveyEvidenceError('INVALID_VAT_RATE')
    if not full_source_gate:raise SurveyEvidenceError('NATIONAL_HOUSEHOLD_INCIDENCE_REQUIRES_VALIDATED_JOINT_DATA')
    rows=list(records)
    if not rows:raise SurveyEvidenceError('EMPTY_JOINT_HOUSEHOLD_DATA')
    if any(not set(REQUIRED_HOUSEHOLD_INCIDENTS)<=z.keys() for z in rows):
        raise SurveyEvidenceError('MISSING_JOINT_TAX_CONSUMPTION_FIELDS')
    origins={x['source_linkage_receipt'] for x in rows}
    if len(origins)!=1 or not next(iter(origins)):
        raise SurveyEvidenceError('LINKAGE_PROVENANCE_NOT_SINGLE_AND_COMPLETE')
    out={}
    for x in rows:
        group=x['household_group'];income=_num(x['base_disposable_income'])
        cons=_num(x['taxable_consumption']);credit=_num(x['vat_credit']);w=_num(x['survey_weight'])
        if w<=0 or cons<0 or credit<0:raise SurveyEvidenceError('INVALID_HOUSEHOLD_INPUT')
        # Tax-exclusive base, fixed consumption, 100% paid price effect.
        burden=cons*r-credit
        o=out.setdefault(group,{'weight':D(0),'weighted_burden':D(0),'weighted_income':D(0),'gainers':D(0)})
        o['weight']+=w;o['weighted_burden']+=burden*w;o['weighted_income']+=income*w
        if burden<0:o['gainers']+=w
    return [{'household_group':k,'weighted_households':str(v['weight']),
         'avg_net_vat_burden_usd':str(v['weighted_burden']/v['weight']),
         'avg_base_disposable_income_usd':str(v['weighted_income']/v['weight']),
         'weighted_fraction_gaining':str(v['gainers']/v['weight']),
         'classification':'CONDITIONAL_RECORD_CALCULATION_NOT_NATIONAL_HOUSEHOLD_INCIDENCE'}
         for k,v in sorted(out.items())]

def streaming_weighted_mean_with_replicates(records, *,value_field,full_weight_field,
                                            replicate_fields,weight_scale='1',
                                            filter_field=None,filter_value=None,
                                            origin_verified=False):
    """O(160) memory streaming mean and official CPS ASEC 160-replicate SE.

    Requires exact 160 column names supplied from the source dictionary, and
    true/original bytes plus independently validated sample eligibility before
    the result can be described as a representative descriptive estimate.
    `origin_verified` is a label request, not proof; callers must call
    primary_ingest_v08.verify_local() separately and retain its hash receipt.
    """
    if len(replicate_fields)!=REPLICATES or len(set(replicate_fields))!=REPLICATES:
        raise SurveyEvidenceError('MUST_MAP_160_DISTINCT_DOCUMENTED_WEIGHT_COLUMNS')
    scale=_num(weight_scale)
    if scale<=0:raise SurveyEvidenceError('INVALID_WEIGHT_SCALE')
    need={value_field,full_weight_field,*replicate_fields}
    if filter_field:need.add(filter_field)
    weighted=D(0); weight=D(0); reps_x=[D(0)]*REPLICATES; reps_w=[D(0)]*REPLICATES
    n=0;total=0
    for rec in records:
        total+=1
        if not need<=rec.keys():raise SurveyEvidenceError('SOURCE_RECORD_MISSING_DOCUMENTED_FIELDS')
        if filter_field and str(rec[filter_field])!=str(filter_value):continue
        n+=1
        x=_num(rec[value_field]);w=_num(rec[full_weight_field])/scale
        if w<0:raise SurveyEvidenceError('NEGATIVE_SURVEY_WEIGHT')
        weight+=w;weighted+=x*w
        for j,k in enumerate(replicate_fields):
            wr=_num(rec[k])/scale
            if wr<0:raise SurveyEvidenceError('NEGATIVE_SURVEY_WEIGHT')
            reps_w[j]+=wr;reps_x[j]+=x*wr
    if n<2 or weight<=0 or any(w<=0 for w in reps_w):
        raise SurveyEvidenceError('INCOMPLETE_OR_ZERO_SURVEY_UNIVERSE')
    point=weighted/weight
    estimates=[u/w for u,w in zip(reps_x,reps_w)]
    stats=replicate_standard_error(point,estimates)
    return {'sample_records_selected':n,'sample_records_scanned':total,
        'sum_household_weights':str(weight), 'estimate':str(point),
        'standard_error':str(stats['standard_error']), 'replicates':REPLICATES,
        'variance_formula':'(4/160)*sum((replicate_mean-full_mean)**2)',
        'data_admission':'SOURCE_BYTES_EXPLICITLY_NEED_EXTERNAL_VERIFICATION' if not origin_verified
            else 'UNVERIFIED_ORIGIN_VERIFIER_RESULT_NOT_PASSED_TO_ESTIMATOR',
        'classification':'SURVEY_DESCRIPTIVE_ESTIMATE_NOT_REFORM_INCIDENCE'}
