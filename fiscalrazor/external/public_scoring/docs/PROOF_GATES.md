# Audit gates, score credibility ladder, and complete-package acceptance criteria

**Zero fabrication policy:** A fiscal reform item is `UNSCORED` unless (1) the legislative provision is defined, (2) matching baseline vintage and years are clear, (3) its fiscal channels are identified, (4) it has a citable official or independently validated model output, (5) interactions are independently resolved, and (6) its uncertainty and limitations are disclosed. Do not estimate nonexistence of data as zero cost. Do not insert a flat haircut, arbitrary growth multiplier, or an unsupported effective interest rate.

## Four credibility levels

- **Official agency estimate**: published CBO/JCT, SSA or CMS score for *precisely the same* policy, years, and assumptions. Limited component scores are official **only within their designated scope**; official SSA 75-year actuarial change is not an official ten-year unified-budget score.
- **Public model reproduction**: exact replay of an agency-released executable tool with pinned version, inputs, build logs and checksums; if public model describes itself as simplified, reproduce its caveats too.
- **Independent validated estimate**: public microdata/calculator validated against multiple out-of-sample released official decisions and accounting/revenue benchmarks, explicit uncertainty intervals; not agency score.
- **Research-only scenario / unscored**: hypothesized behavior or unverified policy assumptions; never insert into an allegedly established savings number.

## Mandatory checks prior to even a *research* aggregate

1. **Data integrity**: URLs, access, source vintage and units; SHA-256 for each downloaded byte stream; 2026 CBO baseline 11 years exact match, with code `python run.py check-official-cbo --path downloads/cbo_annual.csv`.
2. **Source coherence**: no 2026 CBO FY + 2025 CBO FY blend. SSA and CMS are mostly calendar-year, and CBO FY tax detail is fiscal-year. Explicit bridge for each tax and spending cash channel.
3. **No account double-counting**: disallow duplicate fiscal line/account/year ownership and duplicate spending/tax bases. One component may affect another; rerun joint models rather than merely summing published single-provision scores.
4. **Timing**: amounts must be federal cash receipts/outlays when claiming deficit impacts. CBO detailed budget authority is not outlays; policy tax *liability* is not necessarily receipts; 75-year changes are not 10-year fiscal savings.
5. **Real response mechanisms**: tax shifting, form of business, benefit uptake, provider supply, implementation costs, payer substitution, plan bidding and demographic migration. Do not multiply a gross target by a universal percentage.
6. **Trust fund solvency accounting**: separately display OASI/DI, Medicare HI and SMI. Intergovernmental trust fund transfers can change recorded financing without freeing general-government cash. Do not label a tax increase an outlay reduction.
7. **Fiscal feedback**: annual budget interest, GDP, interest rate, debt-stock / deficit flow consistency. The CBO debt-service tool has a less-than-$1T per-year input bound and fixed rates; the BFM has a small-variation scope.
8. **Independent benchmark replay**: JCT published illustrative corporate components; real policy score cases; SSA E2.5 and E1.10/B1.2 year series; CMS annual HI/B/D actuals and forecasts; historical holdout not used for fitting.
9. **Distribution**: weighted household microsimulation and at least low/middle/high income group impacts, net of VAT rebates, premiums and benefit changes; BLS CE data-quality correction for 2025 lapse.
10. **Nontrivial uncertainty**: alternative model parameters, years and baseline revisions, tax elasticities, institutional limits. State what cannot be scored with available data.

**Currently passed by this starter:** 11-year CBO aggregate excerpt accounting identities; 2026 SSA three option series transcribed with base units preserved; JCT ten-line illustrative arithmetic; source registry uniqueness. Tests are local data/arithmetic checks, **not** independent policy reproduction. All 12 reform workstreams are marked `UNSCORED` by design. The complete 2026 CBO CSV and other original downloadable files have not been fetched in this restricted runtime; fetching and byte hashing are reproducible tasks for a network-connected host.

## Milestones toward a proper score

A. Direct exact CBO baseline data hashed and reconciled to its official schemas. B. Tax unit-level 2022→2036 reweighting pinned, validated and compared with individual/corporate JCT examples. C. VAT BEA and BLS category-precise base with household microsimulation and observed expenditure reconciliation. D. SSA 2026 baseline and three 2026 proposals independently recomputed by calendar year; then *combined* OASDI proposal. E. CMS Part A/B/D by population and service category; independent MedPAC payment comparisons. F. Defense spending pipeline and Medicare/SSA cash year bridges. G. Joint noninterest interactions and behavioral/dynamic sensitivities with source-provenance ledger. H. CBO debt-service integration within published valid domain; independent extrapolation flagged otherwise. I. Published reproducible ten-year budget table, 75-year SSA/HI table, distributional table with error envelopes. J. Request official scoring through a Member of Congress or authorized congressional committee with exact legislative text and frozen methodological appendices. These milestones should be audited as separately completed, failed or open—not waved away as a percentage of progress.

## Ways to obtain nonconfidential gaps

- Request publication or explanation of nonconfidential model assumptions and calibration procedures via CBO Office of Communications (`communications@cbo.gov`), emphasizing the exact series and vintage.
- Consult JCT published estimates/methods. A Member may request the official JCT tax score and decide to publicly release it; an outsider's request is not the same as a formal congressional score.
- Use SSA Office of the Chief Actuary published change-provision letters and tables, including exact policy start dates, benefit-credit rules and annual intermediate-case costs; seek the unavailable option combination as a separately requested analysis.
- Ask CMS OACT for the expanded annual tables, detailed HI/SMI sensitivity assumptions and available public actuarial memoranda, observing restrictions on beneficiary-identifying administrative records.
- Avoid claiming that an ordinary public-record request confers entitlement to confidential IRC §6103 taxpayer information or unpublished legislator-request analyses.
