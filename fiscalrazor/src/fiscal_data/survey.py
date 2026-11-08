"""Census CPS ASEC successive-difference-replication (SDR) variance.

The 160-replicate and 4/160 factors are documented in the Census CPS ASEC
technical documentation. This module processes *precomputed point and replicate
statistics*, not fabricated replicate household weights or fictitious estimates.

No variance is inferred if any of the 160 replicates is absent or malformed.
The output is a design-based sampling standard error, not a model-estimation
uncertainty estimate. Source: https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html
"""
from __future__ import annotations
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
D=Decimal
COUNT=160
FACTOR=D(4)/D(COUNT)


def _finite(v):
    try: x=D(str(v))
    except (InvalidOperation, ValueError) as e: raise ValueError('NON_NUMERIC_REPLICATE_ESTIMATE') from e
    if not x.is_finite(): raise ValueError('NON_FINITE_REPLICATE_ESTIMATE')
    return x


def census_asec_sdr(full_estimate, replicate_estimates):
    """Return sampling variance/SE with all 160 genuine replicate estimates.

    The caller must form EACH replicate estimate from the same statistic with
    that replicate's official weights, preserving numerator/denominator logic.
    """
    point=_finite(full_estimate)
    if len(replicate_estimates)!=COUNT:
        raise ValueError(f'EXACTLY_{COUNT}_REPLICATES_REQUIRED')
    replicates=[_finite(x) for x in replicate_estimates]
    variance=FACTOR*sum(((x-point)**2 for x in replicates),D(0))
    return {'full_estimate':point,'variance':variance,'sampling_standard_error':variance.sqrt(),
            'replicates':COUNT,'variance_factor':FACTOR,
            'scope':'CPS_ASEC_SAMPLING_VARIANCE_ONLY_NOT_TOTAL_POLICY_UNCERTAINTY'}


def load_asec_replicate_estimates(path:Path):
    """CSV with one row per 1-indexed replicate: replicate_index,estimate.

    Accept exactly 160 records, unique indices 1..160, no extras. The CSV is a
    pipeline intermediate made from official replicate weights and provenance.
    """
    with open(path,encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not {'replicate_index','estimate'}.issubset(reader.fieldnames):
            raise ValueError('REQUIRED_REPLICATE_COLUMNS_MISSING')
        rows=list(reader)
    if len(rows)!=COUNT: raise ValueError('EXACTLY_160_REPLICATES_REQUIRED')
    estimates={}
    for row in rows:
        try: i=int(row['replicate_index'])
        except (ValueError,TypeError) as e: raise ValueError('INVALID_REPLICATE_INDEX') from e
        if str(i)!=row['replicate_index'] or not 1<=i<=COUNT or i in estimates:
            raise ValueError('DUPLICATE_OR_OUT_OF_RANGE_REPLICATE_INDEX')
        estimates[i]=_finite(row['estimate'])
    return [estimates[i] for i in range(1,COUNT+1)]
