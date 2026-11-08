import json,tempfile,unittest
from pathlib import Path
from fiscal_data.v11_joint import Unidentified
from scripts.evaluate_joint_records_v11 import process

class TestRunner(unittest.TestCase):
    def test_streamed_records_no_national_score(self):
        c={'record_id':'fake_001','calendar_year':2028,
          'filing_status':'single','household_is_one_tax_unit':True,
          'baseline_tax_unit_magi_usd':'50000','official_oasdi_wage_base_usd':'190000',
          'persons':[{'id':'personX','employers':[{'id':'employerA','cash_wages_usd':'50000',
            'covered_under_OASDI_and_HI':True}]}],
          'baseline_income_tax_before_reform_usd':'1000',
          'income_tax_after_health_inclusion_before_other_sections_usd':'1000'}
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'in.jsonl';o=Path(td)/'out.jsonl'
            f.write_text(json.dumps(c)+'\n',encoding='utf8')
            receipt=process(f,o)
            self.assertEqual(receipt['record_count'],1)
            self.assertFalse(receipt['survey_weighting_performed'])
            self.assertEqual(receipt['population_or_national_score'],'NOT_CALCULATED')
            entry=json.loads(o.read_text())
            self.assertEqual(entry['record_id'],'fake_001')
            self.assertIsNone(entry['result']['full_12_provision_result'])
    def test_invalid_record_fails_without_publishing_partial_output(self):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'in.jsonl';o=Path(td)/'out.jsonl'
            f.write_text('{"record_id":"foo","calendar_year":2028}\n',encoding='utf8')
            with self.assertRaises(Unidentified):process(f,o)
            self.assertFalse(o.exists())
    def test_duplicate_id_fails_closed(self):
        c={'record_id':'bad'}
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'in.jsonl';o=Path(td)/'out.jsonl'
            f.write_text(json.dumps(c)+'\n'+json.dumps(c)+'\n',encoding='utf8')
            with self.assertRaises(Unidentified):process(f,o)
            self.assertFalse(o.exists())
    def test_bad_pii_like_id_rejected(self):
        c={'record_id':'john@example.com'}
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'in.jsonl';o=Path(td)/'out.jsonl'
            f.write_text(json.dumps(c)+'\n',encoding='utf8')
            with self.assertRaises(Unidentified):process(f,o)
            self.assertFalse(o.exists())

if __name__=='__main__':unittest.main()
