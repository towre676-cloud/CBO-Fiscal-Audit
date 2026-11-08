"""Raw CBO CSV ingestion and source extract matching.
Preserves unknown raw fields; validates 231 selected values independently on full-file import.
"""
import csv
from decimal import Decimal
from pathlib import Path
from .accounting import read_budget
from .acquisition import BASE, AcquisitionError, verify_local,registry

def validate_full_source(path=None):
    if path is None:
        res=verify_local('cbo_budget_10yr')
        path=BASE/res['local_path']
    with open(path,encoding='utf-8-sig',newline='') as f:
        data=list(csv.DictReader(f))
    if not data or not {'date','variable','value'}.issubset(data[0]):
        raise ValueError('Expected canonical long-form CBO columns date,variable,value')
    values={}
    for row in data:
        key=(row['date'],row['variable'])
        if key in values:raise ValueError('Repeated CBO series/year '+str(key))
        values[key]=Decimal(row['value'])
    extract=read_budget()
    count=0
    for year,variables in extract.items():
        for name,expected in variables.items():
            actual=values.get((f'FY{year}',name))
            if actual is None or abs(actual-expected)>Decimal('0.00000001'):
                raise ValueError(f'EXTRACT_DIFFERS_FROM_ORIGINAL FY{year} {name}: {actual} != {expected}')
            count+=1
    if count!=231:raise ValueError('Expected 231 checked observations')
    return {'full_rows':len(data),'checked_selected_cells':count,'state':'RAW_SOURCE_AND_EXTRACT_MATCH'}
