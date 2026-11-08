from __future__ import annotations
import unittest, io,csv,hashlib,json,tempfile,zipfile
from pathlib import Path
from decimal import Decimal
from fiscal_data.primary_ingest_v08 import (
 OriginalSourceError,source_specs,checked_spec,verify_payload,verify_local,status,
 weighted_household_income_2026,soi_2023_aggregate_checks,final_outlay_checks)
from fiscal_data.v07_calibration import pins,git_blob_sha1

class TestPrimarySourceV08(unittest.TestCase):
 def test_all_18_verified_cbo_pins_present(self):
  self.assertEqual(len(pins()),18)
  self.assertEqual(sum(x['expected_csv_rows'] for x in pins()),97459)
  self.assertEqual(len({x['path'] for x in pins()}),18)
 def test_all_sources_has_public_kind_and_page(self):
  specs=source_specs();self.assertEqual(len(specs),27)
  for k,v in specs.items():
   self.assertIn(v['kind'],('csv','zip'))
   self.assertIn('source',v['catalog_status'].lower().replace('official_repository_git_sha_confirmed','source')) if k.startswith('cbo_') else None
   self.assertTrue(v['page'].startswith('https://'))
 def test_missing_originals_fail_closed(self):
  with tempfile.TemporaryDirectory() as td:
   self.assertEqual(sum(r['state']=='VERIFIED_ORIGINAL_LOCAL' for r in status(td)),0)
   with self.assertRaisesRegex(OriginalSourceError,'NOT_ACQUIRED'):verify_local('cbo_01',td)
 def test_plain_csv_integrity(self):
  b=b'date,variable,value\nFY2036,deficit,-100\n';sha=git_blob_sha1(b)
  s={'kind':'csv','expected_git_blob_sha1':sha,'expected_csv_rows':1}
  self.assertEqual(verify_payload(b,s)['git_blob_sha1'],sha)
  with self.assertRaisesRegex(OriginalSourceError,'GIT_BLOB_SHA1_MISMATCH'):verify_payload(b.replace(b'-100',b'-101'),s)
 def test_html_rejected(self):
  with self.assertRaisesRegex(OriginalSourceError,'HTML_OR_XML_NOT_DATA'):verify_payload(b'<!DOCTYPE html><html>Denied</html>',{'kind':'csv'})
 def test_duplicate_csv_header_rejected(self):
  with self.assertRaisesRegex(OriginalSourceError,'BAD_CSV_HEADER'):verify_payload(b'a,a,c\n1,2,3\n',{'kind':'csv'})
 def test_missing_source_zip_rejected(self):
  with self.assertRaisesRegex(OriginalSourceError,'BAD_ZIP_MAGIC'):verify_payload(b'Not zip',{'kind':'zip'})
 def test_zip_crc_rejected(self):
  mem=io.BytesIO()
  with zipfile.ZipFile(mem,'w') as z:z.writestr('x.csv','a,b,c\n1,2,3\n')
  b=bytearray(mem.getvalue())
  loc=b.find(b'1,2,3')
  self.assertGreater(loc,0);b[loc]=ord('2')
  with self.assertRaisesRegex(OriginalSourceError,'ZIP_CRC_FAILURE'):verify_payload(bytes(b),{'kind':'zip'})
 def test_zip_member_traversal_rejected(self):
  mem=io.BytesIO()
  with zipfile.ZipFile(mem,'w') as z:z.writestr('../unsafe.csv','x,y,z\n1,2,3\n')
  with self.assertRaisesRegex(OriginalSourceError,'UNSAFE_ZIP_MEMBER'):verify_payload(mem.getvalue(),{'kind':'zip'})
 def test_cps_cannot_simulate_missing_archives(self):
  with self.assertRaisesRegex(OriginalSourceError,'CPS_ORIGINAL_NOT_MATERIALIZED'):weighted_household_income_2026('/never/exists.zip','house.csv')
 def test_cps_missing_known_fields_fails(self):
  with tempfile.TemporaryDirectory() as td:
   z=Path(td)/'source.zip'
   with zipfile.ZipFile(z,'w') as arc:arc.writestr('house.csv','foo,bar\n1,2\n')
   with self.assertRaisesRegex(OriginalSourceError,'REQUIRED_FIELDS'):weighted_household_income_2026(z,'house.csv')
 def test_cps_wrong_population_fails(self):
  with tempfile.TemporaryDirectory() as td:
   z=Path(td)/'cps.zip'
   with zipfile.ZipFile(z,'w') as arc:arc.writestr('house.csv','H_IDNUM,HSUP_WGT,HTOTVAL,HPCTCUT,H_HHTYPE\nA,250000,65000,1,1\n')
   with self.assertRaisesRegex(OriginalSourceError,'COUNT_MISMATCH'):weighted_household_income_2026(z,'house.csv')
 def test_irscsv_cannot_be_called_individual_microdata(self):
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'irs.csv';f.write_text('STATE,ZIPCODE,AGI_STUB,N1,A00100\nCT,06798,1,2,100\n')
   with self.assertRaisesRegex(OriginalSourceError,'AGGREGATE_INCOMPLETE'):soi_2023_aggregate_checks(f)
 def test_irscsv_needs_explicit_data_columns(self):
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'irs.csv';f.write_text('zipcode,income\n12345,4\n')
   with self.assertRaisesRegex(OriginalSourceError,'SOI_SCHEMA'):soi_2023_aggregate_checks(f)
 def test_source_url_must_be_https(self):
  with self.assertRaisesRegex(OriginalSourceError,'ONLY_PUBLIC_HTTPS'):checked_spec('external',{'url':'http://example.com/data.csv'})
 def test_cbo_host_locked(self):
  with self.assertRaisesRegex(OriginalSourceError,'CBO_HOST'):checked_spec('cbo_01',{'url':'https://example.com/data.csv'})
 def test_source_cannot_rename_country_population(self):
  sp=source_specs();self.assertNotEqual(sp['cps_asec_2026_csv']['unit'],sp['irs_soi_2023_zip_agi']['unit'])

 def test_cps_2026_full_vs_interviewed_universe(self):
  # Source-grounded IPUMS/Census reference: 88,026 household entries; 53,321 interviewed.
  with tempfile.TemporaryDirectory() as td:
   z=Path(td)/'cps.zip'
   import itertools
   hdr='H_IDNUM,HSUP_WGT,HTOTVAL,HPCTCUT,H_HHTYPE\n'
   with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED) as arc:
    with arc.open('hhpub26.csv','w') as sink:
     sink.write(hdr.encode())
     for i in range(88026):
      if i<53321: row=f'H{i:08},250000,{65000+i%50},{1+i%20},1\n'
      else: row=f'H{i:08},0,0,0,2\n'
      sink.write(row.encode())
   r=weighted_household_income_2026(z,'hhpub26.csv')
   self.assertEqual(r['all_household_records'],88026)
   self.assertEqual(r['interviewed_household_records'],53321)
   self.assertEqual(len(r['by_income_5pct']),20)
   self.assertEqual(Decimal(r['weighted_interviewed_households']),Decimal('133302500'))

 def test_cps_2026_older_wrong_field_names_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   z=Path(td)/'cps.zip'
   with zipfile.ZipFile(z,'w') as arc:
    arc.writestr('house.csv','H_IDNUM,HSUP_WGT,HTOTVAL8,HPCTCUT2,H_HHTYPE\nH0,250000,100,1,1\n')
   with self.assertRaisesRegex(OriginalSourceError,'REQUIRED_FIELDS'):
    weighted_household_income_2026(z,'house.csv')


 def test_unpinned_local_source_requires_origin_receipt(self):
  with tempfile.TemporaryDirectory() as td:
   from fiscal_data.primary_ingest_v08 import destination
   spec=source_specs()['cms_medicare_2026_expanded']
   loc=destination(td,'cms_medicare_2026_expanded',spec)
   with zipfile.ZipFile(loc,'w') as z:z.writestr('spreadsheet.xlsx','fake data')
   self.assertEqual([x for x in status(td) if x['id']=='cms_medicare_2026_expanded'][0]['state'],'LOCAL_BYTES_UNVERIFIED')
   with self.assertRaisesRegex(OriginalSourceError,'ORIGINAL_PROVENANCE_RECEIPT'):
    verify_local('cms_medicare_2026_expanded',td)

 def test_official_source_csv_empty_rejected(self):
  with self.assertRaisesRegex(OriginalSourceError,'CSV_HAS_NO_RECORDS'):
   verify_payload(b'date,variable,value\n',{'kind':'csv'})

 def test_symlink_not_admitted_as_original(self):
  with tempfile.TemporaryDirectory() as td:
   from fiscal_data.primary_ingest_v08 import destination
   origin=Path(td)/'external.csv';origin.write_text('date,variable,value\nX,y,4\n')
   link=destination(td,'cbo_11',source_specs()['cbo_11'])
   link.symlink_to(origin)
   with self.assertRaisesRegex(OriginalSourceError,'SYMLINK_AS_ORIGINAL'):
    verify_local('cbo_11',td)

 def test_local_bytes_exceed_policy_size_limit(self):
  with self.assertRaisesRegex(OriginalSourceError,'APPROVED_SIZE_LIMIT'):
   verify_payload(b'x'*50,{'kind':'csv','max_bytes':40})

 def test_large_public_use_sample_not_replaced_by_tiny_fake_zip(self):
  with tempfile.TemporaryDirectory() as td:
   z=Path(td)/'fake.zip'
   with zipfile.ZipFile(z,'w') as arc:arc.writestr('hh.csv','H_IDNUM\n1\n')
   with self.assertRaisesRegex(OriginalSourceError,'SOURCE_TOO_SMALL'):
    verify_payload(z.read_bytes(),source_specs()['cps_asec_2026_csv'])


 def test_origin_https_acquisition_receipt_then_local_replay(self):
  # Simulated transfer exercises the full production read/write path; NOT real government data.
  from fiscal_data.primary_ingest_v08 import download_source,verify_local,destination
  from unittest.mock import patch
  data=('STATE,ZIPCODE,AGI_STUB,N1,A00100\n'+'CT,06798,1,2,100\n'*1800).encode()
  self.assertGreater(len(data),10000)
  spec=source_specs()['irs_soi_2023_state_shares']
  class MockHttp:
   def __init__(self): self.pos=0;self.headers={'Content-Length':str(len(data))}
   def __enter__(self): return self
   def __exit__(self,*args): return False
   def geturl(self): return spec['url']
   def read(self,n):
    x=data[self.pos:self.pos+n];self.pos+=len(x);return x
  with tempfile.TemporaryDirectory() as td:
   with patch('fiscal_data.primary_ingest_v08.urllib.request.urlopen',return_value=MockHttp()):
    receipt=download_source('irs_soi_2023_state_shares',td)
   self.assertEqual(receipt['bytes'],len(data))
   verified=verify_local('irs_soi_2023_state_shares',td)
   self.assertEqual(verified['sha256'],hashlib.sha256(data).hexdigest())
   self.assertIn('HTTPS_ORIGIN',verified['provenance_class'])
   d=destination(td,'irs_soi_2023_state_shares',spec)
   origin=d.with_suffix(d.suffix+'.origin.json')
   m=json.loads(origin.read_text());m['bytes']+=1;origin.write_text(json.dumps(m))
   with self.assertRaisesRegex(OriginalSourceError,'ORIGIN_PROVENANCE_MISMATCH'):
    verify_local('irs_soi_2023_state_shares',td)

 def test_origin_redirect_to_unrelated_host_denied(self):
  from fiscal_data.primary_ingest_v08 import download_source
  from unittest.mock import patch
  class MockHttp:
   headers={'Content-Length':'100'}
   def __enter__(self): return self
   def __exit__(self,*args): return False
   def geturl(self): return 'https://evil.example.com/false.csv'
  with tempfile.TemporaryDirectory() as td:
   with patch('fiscal_data.primary_ingest_v08.urllib.request.urlopen',return_value=MockHttp()):
    with self.assertRaisesRegex(OriginalSourceError,'REDIRECT_HOST'):
     download_source('irs_soi_2023_state_shares',td)

 def test_irs_aggregate_rows_cannot_replace_tax_units(self):
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'irs.csv';f.write_text('STATE,ZIPCODE,AGI_STUB,N1,A00100\n'+'CT,06798,1,2,100\n'*1001)
   r=soi_2023_aggregate_checks(f)
   self.assertIn('NOT_INDIVIDUAL_TAX_UNITS',r['classification'])

if __name__=='__main__':unittest.main()
