from pathlib import Path
import tempfile,unittest,zipfile,io,csv
from fiscal_data.cps_preflight import inspect_archive,CPSDataError
class CPSTests(unittest.TestCase):
    def test_nonexistent_archive_is_not_counted(self):
        with self.assertRaises(CPSDataError):inspect_archive('/missing/2026_census.zip')
    def test_zip_member_inventory_not_microdata_claim(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'small.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('source.csv','id,weight\n1,20\n')
            r=inspect_archive(p)
            self.assertEqual(r['status'],'SOURCE_ARCHIVE_INSPECTED_NOT_YET_POLICY_SCORED')
            self.assertNotIn('validated_2026_record_counts',r)
    def test_refuse_path_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('../outside.txt','stuff')
            with self.assertRaises(CPSDataError):inspect_archive(p)
    def test_refuse_unverified_record_counts(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'small.zip'
            with zipfile.ZipFile(p,'w') as z:
                for x in ('household','family','person'):z.writestr(x+'.csv','id,weight\n1,20\n')
            with self.assertRaises(CPSDataError):inspect_archive(p,{x:x+'.csv' for x in ('household','family','person')})
    def test_refuse_duplicate_member_identity(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'small.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('all.csv','id,weight\n1,20\n')
            with self.assertRaises(CPSDataError):inspect_archive(p,{x:'all.csv' for x in ('household','family','person')})
