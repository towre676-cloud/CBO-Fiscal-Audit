#!/usr/bin/env python3
"""Build transparent source registry. This writes *metadata*, never synthetic datasets."""
import json
from pathlib import Path
from datetime import date
BASE = Path(__file__).resolve().parents[1]
ROOT = 'https://raw.githubusercontent.com/US-CBO/cbo-data/main/'
CBO = [
('cbo_budget_10yr','budget','data/budget/ten_year_budget/annual_fy_2026-02.csv','99f55b63bb8db8c214e2ee08de5ce0c216358fac','ten-year baseline'),
('cbo_budget_longterm','budget','data/budget/long_term_budget/annual_fy_2026-02.csv','d783ad369ea86b9d2fbf2b26776b462ee4756662','30-year federal budget'),
('cbo_budget_history','budget','data/budget/historical_budget/annual_fy_2026-02.csv','a93887a03724caaf45fee10fc17d618cee9d8b0e','budget history'),
('cbo_trust_funds','trust_fund','data/budget/trust_fund/annual_fy_2026-02.csv','e3d8035b59a85be3ea039a1e22a1491574426eb6','trust fund projections, fiscal years'),
('cbo_revenue_detail','tax','data/budget/revenue_detail/annual_fy_2026-02.csv','73b65c16e72c84ec67ef4838242727db19683d5a','revenue components'),
('cbo_spending_detail','spending','data/budget/spending_detail/annual_fy_2026-02.csv','1022b8c75fee56293df2e1911d25cf99d75a3c99','budget account level'),
('cbo_tax_parameters','tax','data/budget/tax_parameters/annual_cy_2026-02.csv','f404f6bd2e6868370f5fa0ff1b39be033b0a2432','federal tax parameters'),
('cbo_automatic_stabilizers','macro','data/budget/automatic_stabilizers/annual_fy_2024-11.csv','ce99a27dbdfb48a3c10e7e69cc7ed4a1f53dfdd7','automatic stabilizers; 2024 vintage'),
('cbo_econ_quarterly','macro','data/economic/historical_economic/quarterly_2026-02.csv','c2df8394b5234b4aa831e1b61ce37a45ac5671e9','historical and projected series'),
('cbo_econ_fiscal','macro','data/economic/economic_projections/fiscal_2026-02.csv','64318ea37595af4edacee81691256d711fb63707','fiscal-year macro projections'),
('cbo_econ_calendar','macro','data/economic/economic_projections/calendar_2026-02.csv','6d5cd08bb44b4dcda5d9a7f7db31b220cfa15ded','calendar-year macro projections'),
('cbo_econ_quarterly_projection','macro','data/economic/economic_projections/quarterly_2026-02.csv','c4f63ddda98f23070b704f55e0ac87a776117c8f','quarterly macro projections'),
('cbo_longterm_levels','macro','data/economic/long_term_economic/levels_2026-02.csv','3b0d13b1fff5f3250fd7d670b5367c1ba96abdde','long-term levels'),
('cbo_longterm_rates','macro','data/economic/long_term_economic/rates_2026-02.csv','6718440bb25f9afb261412dc5ea6b908a7170f03','long-term growth rates'),
('cbo_lfp_rates','labor','data/economic/long_term_economic/lfp_rates_2026-02.csv','45bb06e63748ebd376cc8f0c6081be5938df49ef','labor participation'),
('cbo_fertility','demography','data/economic/demographic/fertility_2026-01.csv','cc99271f661b8876e82e11117e455e593b482bc4','fertility projection vintage 2026-01'),
('cbo_migration','demography','data/economic/demographic/migration_2026-01.csv','e316a2691e7171f3cf6bb2ffc7cf3afd45dec2ad','migration projection vintage 2026-01'),
('cbo_mortality','demography','data/economic/demographic/mortality_2026-01.csv','cc58aec6e3be8ac50a3dfca4cbdec7a39f8989c7','mortality projection vintage 2026-01'),
('cbo_population','demography','data/economic/demographic/population_census_2026-01.csv','58e04f480a4800a488f706ee666a899204f6db01','Census-basis population projection'),
('cbo_ss_population','demography','data/economic/demographic/ss_area_population_2026-01.csv','065b262bfea0be0eaadf64471c89079614564f07','SSA area population projection'),
]
entries=[]
for sid,cat,path,sha,desc in CBO:
    entries.append(dict(id=sid,agency='CBO',category=cat,description=desc,source_kind='official_CBO_GitHub_machine_readable',landing_url='https://www.cbo.gov/data/budget-economic-data',download_url=ROOT+path,expected_git_blob_sha1=sha,fetch_mode='download',local_path='data/raw/'+sid+'/'+Path(path).name,vintage=Path(path).stem.split('_')[-1],access_status='GITHUB_METADATA_CONFIRMED_BYTES_NOT_ACQUIRED'))
def add(id, agency,cat,desc,url,landing=None,mode='download',notes=None,local=None):
    entries.append(dict(id=id,agency=agency,category=cat,description=desc,source_kind='agency_primary',landing_url=landing or url,download_url=url if mode=='download' else None,expected_git_blob_sha1=None,fetch_mode=mode,local_path=local,access_status='OFFICIAL_URL_VERIFIED_BYTES_NOT_ACQUIRED',notes=notes or ''))
add('ssa_oasdi_2026_excel','SSA','trust_fund','SSA 2026 Trustees single year Excel Tables (2026-2100)','https://www.ssa.gov/oact/tr/2026/SingleYearTRTables_TR2026.xlsx','https://www.ssa.gov/oact/tr/2026/lrIndex.html')
add('ssa_oasdi_ivb1_html','SSA','trust_fund','SSA 2026 table IV.B1; OASI DI OASDI separate 1970-2100','https://www.ssa.gov/oact/tr/2026/lr4b1.html','https://www.ssa.gov/oact/tr/2026/lrIndex.html')
add('ssa_oasdi_operations_html','SSA','trust_fund','SSA 2026 VI.G2 combined operations (illustrative)','https://www.ssa.gov/oact/tr/2026/lr6g2.html','https://www.ssa.gov/oact/tr/2026/lrIndex.html')
add('ssa_trustee_summary_2026','SSA/CMS','trust_fund','Combined SSA CMS 2026 trustees summary with separate trust fund actuarial results','https://www.ssa.gov/oact/trsum/')
add('cms_trustees_2026','CMS','health','2026 Medicare Trustees Report expanded and supplementary actuarial tables (CMS ZIP)','https://www.cms.gov/files/zip/2026-expanded-supplementary-tables-figures.zip','https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds')
add('cps_asec_2026_csv','Census','households','March 2026 CPS ASEC CSV public-use microdata, includes replicate weights','https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asecpub26csv.zip','https://www.census.gov/data/datasets/time-series/demo/cps/cps-asec.2026.html')
add('cps_asec_2026_fixed','Census','households','March 2026 CPS ASEC original fixed-width public use','https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asec2026_pubuse.dat.gz','https://www.census.gov/data/datasets/time-series/demo/cps/cps-asec.2026.html')
add('cps_asec_2026_repwgt','Census','households','March 2026 CPS ASEC external replicate weights','https://www2.census.gov/programs-surveys/cps/datasets/2026/march/CPS_ASEC_ASCII_REPWGT_2026.DAT.GZ','https://www.census.gov/data/datasets/time-series/demo/cps/cps-asec.2026.html')
add('cps_asec_2026_layout','Census','households','March 2026 CPS ASEC person record fixed-format documentation','https://www2.census.gov/programs-surveys/cps/datasets/2026/march/persfmt.txt')
add('cps_asec_2026_dictionary','Census','households','March 2026 CPS ASEC full data dictionary PDF','https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asec2026_ddl_pub_full.pdf')
add('cbo_household_research_2023','CBO','households','CBO 2023 household income distribution researcher data released Sept 2026','https://www.cbo.gov/system/files/2026-09/62761-additional-data-for-researchers.zip','https://www.cbo.gov/publication/62761')
add('cbo_household_figures_2023','CBO','households','CBO figure underlying dataset','https://www.cbo.gov/system/files/2026-09/62761-data.xlsx','https://www.cbo.gov/publication/62761')
add('cbo_household_supp_2023','CBO','households','CBO household supplemental data','https://www.cbo.gov/system/files/2026-09/62761-supp-data.xlsx','https://www.cbo.gov/publication/62761')
add('jct_tax_expenditures_2025_2029','JCT','tax','Official fiscal 2025-29 tax expenditure estimates, distribution by class','https://www.jct.gov/getattachment/fe301c56-965c-48c9-ac06-52b7b6765b05/x-45-25.pdf','https://www.jct.gov/')
add('treasury_tax_expenditures_fy2027','Treasury','tax','FY2027 Treasury tax expenditures Excel', 'https://home.treasury.gov/policy-issues/tax-policy/tax-expenditures/',mode='manual_landing')
add('treasury_mts_api','Treasury FiscalData','actuals','Monthly Treasury Statement 1-6c live official fiscal data APIs','https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_1',mode='api',notes='API pagination and reporting-date filter required; https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/')
add('irs_soi_zip2023','IRS','tax','SOI individual ZIP-level federal income tax data latest confirmed TY2023','https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-zip-code-data-soi',mode='manual_landing',notes='Aggregates by ZIP and income, not individual household microdata; statistical disclosure controls apply')
add('cms_provider_services_2024','CMS','health','2024 Medicare Part B provider-and-service payments and utilization','https://data.cms.gov/sites/default/files/2026-05/b5ebab5a-f490-418a-9bce-4b9f31419356/PHY_R26_P05_V10_D24_Prov_Svc.csv','https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners')
add('omb_historical_tables','OMB','budget','Budget historical tables, actual and proposed fiscal accounts','https://www.whitehouse.gov/omb/budget/historical-tables/',mode='manual_landing')
add('bls_cpi','BLS','macro','Consumer Price Index primary data and time series','https://download.bls.gov/pub/time.series/cu/',mode='manual_landing')
add('bea_nipa','BEA','macro','National Income and Product Accounts GDP and incomes','https://www.bea.gov/data/gdp/gross-domestic-product',mode='manual_landing')
add('census_acs_pums','Census','households','American Community Survey PUMS households and persons','https://www.census.gov/programs-surveys/acs/microdata.html',mode='manual_landing')
add('census_sipp','Census','households','Survey of Income and Program Participation public use','https://www.census.gov/programs-surveys/sipp/data/datasets.html',mode='manual_landing')
add('fed_scf','Federal Reserve','households','Survey of Consumer Finances households and weights','https://www.federalreserve.gov/econres/scfindex.htm',mode='manual_landing')
add('usaspending','Treasury','spending','USAspending detailed award and account data','https://www.usaspending.gov/download_center/custom_award_data',mode='manual_landing')
add('tax_calculator_psl','Policy Simulation Library','tax_model','Tax-Calculator 6.9.0, independently-developed microsimulation tool','https://taxcalc.pslmodels.org/',mode='manual_landing',notes='Software is not agency score; filing-unit dataset and microsimulation version needed')
(BASE/'data'/'source_catalog.json').write_text(json.dumps({'as_of':'2026-11-06','semantics':'Metadata verification does not imply raw file acquisition or empirical reproduction.','entries':entries},indent=2)+'\n')
print('catalog entries',len(entries),'GitHub pinned',len(CBO))
