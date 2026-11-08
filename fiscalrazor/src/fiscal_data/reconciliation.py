"""A vintage-aware event ledger: events may be documented but are NOT allocated to projection years automatically."""
import csv
from decimal import Decimal
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]

def events():
 with (BASE/'data/projection_reconciliation_events.csv').open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))

def additive_annual_revision(events,year):
 """Never convert cumulative 10-year updates into annual baseline dollars without an annual profile."""
 for event in events:
  if event['period_affected'] in ('FY2027-FY2036',f'FY{year}'):
   if event['model_treatment']!='COMPLETE_ANNUAL_OFFICIAL_PROFILE':
    raise ValueError('NO_ANNUAL_RECONCILIATION_PROFILE: '+event['event_date'])
 raise ValueError('NO_OFFICIAL_ANNUAL_REVISION_DATA_AVAILABLE')
