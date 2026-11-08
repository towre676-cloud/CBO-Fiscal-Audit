import unittest,tempfile,csv
from decimal import Decimal as D
from pathlib import Path
from fiscal_data.v09_capacity import run,original_cbo_pce_if_present, write
from fiscal_data.v09_survey import replicate_standard_error, weighted_mean_with_replicates, conditional_vat_incidence,SurveyEvidenceError
from fiscal_data.primary_ingest_v08 import OriginalSourceError
class TestV09(unittest.TestCase):
 def test_complete_ten_year_pce_source_series(self):
  x=run();self.assertEqual(len(x),10);self.assertEqual([a['fy'] for a in x],list(range(2027,2037)))
 def test_2036_mechanical_vat_stylized(self):
  x=run()[-1];self.assertEqual(D(x['gross_all_pce_mechanical_bn']),D('1599.4815612025'))
  self.assertEqual(D(x['net_after_rebate_mechanical_bn']),D('1279.585248962000'))
  self.assertEqual(D(x['gap_less_mechanical_net_bn']),D('434.437479113000'))
  self.assertAlmostEqual(float(x['minimum_gross_all_pce_rate_to_close_gap_at_current_rebate_share']), 0.0669757145710071, places=13)
 def test_unverified_is_never_original(self):
  self.assertTrue(all('EXCERPT' in a['source_integrity'] for a in run()))
  with self.assertRaises(OriginalSourceError):run(require_originals=True)
 def test_bad_vat_rates_rejected(self):
  for rate in ['-0.01','1.1','NaN','Infinity']:
   with self.subTest(rate=rate),self.assertRaises(OriginalSourceError):run(vat_rate=rate)
 def test_0pct_vat_and_100pct_rebate(self):
  for row in run(vat_rate='0'):
   self.assertEqual(D(row['gross_all_pce_mechanical_bn']),0)
  for row in run(rebate_fraction='1'):
   self.assertEqual(D(row['net_after_rebate_mechanical_bn']),0)
 def test_output_csv_exact_rows(self):
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'output.csv';write(f)
   with f.open(newline='') as i:self.assertEqual(len(list(csv.DictReader(i))),10)
 def test_sensitivity_only_hypothetical(self):
  from fiscal_data.v09_capacity import mechanical_taxable_fraction_scenarios
  scenarios=mechanical_taxable_fraction_scenarios(fractions=['0.5','1.0'])
  self.assertEqual(len(scenarios),20)
  a=[x for x in scenarios if x['fy']==2036]
  self.assertEqual(D(a[0]['hypothetical_net_receipts_bn'])*2,D(a[1]['hypothetical_net_receipts_bn']))
  self.assertIn('STYLIZED_MECHANICAL',a[0]['classification'])
 def test_sensitivity_rejects_nonsensical_shares(self):
  from fiscal_data.v09_capacity import mechanical_taxable_fraction_scenarios
  for f in ['0','-0.1','1.2','NaN']:
   with self.subTest(f=f),self.assertRaises(OriginalSourceError):
    mechanical_taxable_fraction_scenarios(fractions=[f])
 def test_actual_present_but_invalid_fails_closed(self):
  from fiscal_data.v09_capacity import run
  from fiscal_data.primary_ingest_v08 import source_specs,destination
  with tempfile.TemporaryDirectory() as td:
   p=destination(td,'cbo_02',source_specs()['cbo_02']);p.write_bytes(b'corrupted')
   with self.assertRaises(OriginalSourceError):run(raw_root=td)
 def test_sdr_variance_zero(self):
  z=replicate_standard_error('5',['5']*160);self.assertEqual(z['variance'],0)
 def test_sdr_variance_exact(self):
  z=replicate_standard_error('10',['12']*160);self.assertEqual(z['variance'],D('16'))
 def test_sdr_incomplete_fails(self):
  with self.assertRaisesRegex(SurveyEvidenceError,'REQUIRES_160'):replicate_standard_error('5',[6]*159)
 def test_sdr_nonfinite_fails(self):
  with self.assertRaisesRegex(SurveyEvidenceError,'NONFINITE'):replicate_standard_error('2',['NaN']*160)
 def test_mean_replicates_two_records(self):
  cols=[f'w{i}' for i in range(160)];records=[{'x':'2','base':'2',**{k:'2' for k in cols}},
   {'x':'6','base':'1',**{k:'1' for k in cols}}];
  z=weighted_mean_with_replicates(records,value_field='x',full_weight_field='base',replicate_fields=cols)
  self.assertEqual(D(z['estimate']),D(10)/D(3));self.assertEqual(D(z['standard_error']),0)
 def test_mean_missing_field_fails(self):
  cols=[f'w{i}' for i in range(160)]
  with self.assertRaisesRegex(SurveyEvidenceError,'MISSING_DOCUMENTED'):
   weighted_mean_with_replicates([{'x':2,'base':2}],value_field='x',full_weight_field='base',replicate_fields=cols,min_records=1)
 def test_mean_duplicate_columns_fails(self):
  with self.assertRaisesRegex(SurveyEvidenceError,'MUST_MAP_160_DISTINCT'):
   weighted_mean_with_replicates([],value_field='x',full_weight_field='base',replicate_fields=['a']*160)
 def test_no_national_households_without_joint_data(self):
  with self.assertRaisesRegex(SurveyEvidenceError,'REQUIRES_VALIDATED_JOINT'):
   conditional_vat_incidence([{'household_group':1}],rate='0.05')
 def test_incidence_mechanical_fixtures_labeled(self):
  records=[dict(household_group=1,base_disposable_income='10000',taxable_consumption='8000',vat_credit='500',survey_weight='10',source_linkage_receipt='SYNTHETIC_FIXTURE'),
           dict(household_group=2,base_disposable_income='50000',taxable_consumption='10000',vat_credit='100',survey_weight='20',source_linkage_receipt='SYNTHETIC_FIXTURE')]
  ans=conditional_vat_incidence(records,rate='0.05',full_source_gate=True)
  self.assertEqual(D(ans[0]['avg_net_vat_burden_usd']),D('-100'))
  self.assertEqual(D(ans[1]['avg_net_vat_burden_usd']),D('400'))
  self.assertIn('CONDITIONAL',ans[0]['classification'])
if __name__=='__main__':unittest.main()

class TestStreamingSDR(unittest.TestCase):
 def test_streaming_equal_batch(self):
  from fiscal_data.v09_survey import streaming_weighted_mean_with_replicates
  cols=[f'w{i}' for i in range(160)]
  records=[{'income':'100','weight':'2','status':'1',**{c:'2' for c in cols}},
           {'income':'200','weight':'2','status':'1',**{c:'2' for c in cols}},
           {'income':'999','weight':'50','status':'2',**{c:'50' for c in cols}}]
  z=streaming_weighted_mean_with_replicates(iter(records),value_field='income',
     full_weight_field='weight',replicate_fields=cols,filter_field='status',filter_value='1')
  self.assertEqual(D(z['estimate']),D(150))
  self.assertEqual(D(z['standard_error']),D(0))
  self.assertEqual(z['sample_records_selected'],2)
 def test_streaming_replicate_variance(self):
  from fiscal_data.v09_survey import streaming_weighted_mean_with_replicates
  cols=[f'w{i}' for i in range(160)]
  rows=[{'inc':'0','base':'1',**{c:('2' if i<80 else '1') for i,c in enumerate(cols)}},
        {'inc':'100','base':'1',**{c:('1' if i<80 else '2') for i,c in enumerate(cols)}}]
  z=streaming_weighted_mean_with_replicates(rows,value_field='inc',full_weight_field='base',replicate_fields=cols)
  self.assertEqual(D(z['estimate']),D('50'))
  self.assertGreater(D(z['standard_error']),0)
 def test_missing_documented_replicate_fails(self):
  from fiscal_data.v09_survey import streaming_weighted_mean_with_replicates
  with self.assertRaisesRegex(SurveyEvidenceError,'MUST_MAP_160_DISTINCT'):
   streaming_weighted_mean_with_replicates([],value_field='inc',full_weight_field='base',replicate_fields=['a'])
