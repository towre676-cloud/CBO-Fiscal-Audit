import unittest,tempfile
from pathlib import Path
from fiscal_data.acquisition import registry,git_blob_sha1,admit_bytes,AcquisitionError,raw_target,inventory
from fiscal_data.gates import assess,release_combined_score
from fiscal_data.cbo_source import validate_full_source
class AcquisitionTests(unittest.TestCase):
 def test_catalog_has_40_sources(self):self.assertGreaterEqual(len(registry()),40)
 def test_unique_ids(self):self.assertEqual(len(set(registry())),len(registry()))
 def test_sha_computation(self):self.assertEqual(git_blob_sha1(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
 def test_corrupt_git_blob_blocked(self):
  e=registry()['cbo_budget_10yr']
  with self.assertRaisesRegex(AcquisitionError,'SOURCE_BLOB_MISMATCH'):admit_bytes(e,b'fake')
 def test_html_masquerading_csv_blocked(self):
  e={'id':'test','download_url':'https://gov.example/data.csv'}
  with self.assertRaisesRegex(AcquisitionError,'HTML_RETURNED'):admit_bytes(e,b'<html>blocked</html>')
 def test_empty_source_blocked(self):
  with self.assertRaisesRegex(AcquisitionError,'EMPTY'):admit_bytes({'id':'x'},b'')
 def test_zip_magic_blocked(self):
  with self.assertRaisesRegex(AcquisitionError,'ZIP_MAGIC'):admit_bytes({'id':'x','download_url':'https://agency.gov/foo.zip'},b'bad data')
 def test_local_path_policy(self):
  for e in registry().values():
   if e['fetch_mode']=='download':self.assertIn('data/raw',str(raw_target(e)))
 def test_status_does_not_claim_unfetched(self):
  self.assertTrue(all(x['status'] in ('NOT_ACQUIRED','LANDING_OR_API_ONLY') for x in inventory()))
 def test_fail_closed_reform_claim(self):
  self.assertTrue(all(x.status=='BLOCKED' for x in assess({})))
  with self.assertRaisesRegex(ValueError,'NO_OFFICIAL_COMBINED_SCORE'):release_combined_score({})
 def test_official_link_not_sufficient(self):
  d={'official_cbo_combined_score':{'status':'VERIFIED','source_url':'https://www.cbo.gov','source_date':'2026-11-01'}}
  self.assertEqual(next(x for x in assess(d) if x.criterion=='official_cbo_combined_score').status,'PENDING_MANUAL_AUDIT')
