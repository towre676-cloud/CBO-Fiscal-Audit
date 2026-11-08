# Independent review receipt: structural integrity before any score gate can pass

The original score interface demanded a source URL and nonempty review label, but such fields alone can be faked. The expansion introduces `src/receipt_validation.py` which requires a **local verifiable record** bound to each exact submitted policy/interaction CSV row. This does not certify methodology or official status: it only makes arbitrary self-declared review claims materially harder and detects missing inputs/changed calculations.

For each `reproduction_receipt` field supply a relative path under `receipts/` to a JSON file containing:

```
{
  "source_url": "https://agency.gov/path/to/actual/source",
  "baseline_vintage": "2026-02",
  "row_sha256": "64-character SHA-256 of exact canonical row content",
  "source_original_path": "downloads/canonical_original.csv",
  "source_original_sha256": "64-character SHA-256 of downloaded agency source",
  "calculation_code_path": "scripts/calculate_policy.py",
  "calculation_code_sha256": "64-character SHA-256 of inspected program",
  "reviewer": "independent reviewer identifier",
  "independent_review_complete": true
}
```

All entered URLs/hashes/identifiers above are illustrative schema placeholders; **no reviewed policy receipt satisfying this schema is included**. A `row_sha256` is calculated by `src.receipt_validation.row_fingerprint(row)` after excluding the `reproduction_receipt` and `review_status` fields. The source file must exist under `downloads/`, calculation script under `scripts/`, and the hashes must match original file bytes. Accessing `../` outside those directories fails. Raw-source provenance must then be independently checked against agency material; a locally hashed impostor can still pass *structural* hash checks, so the final policy model also needs external evidence and methodological evaluation.

A receipt cannot turn an SSA percentage-point actuarial projection or a synthetic family VAT example into an actual fiscal-year cash effect. `src/score_gate.py` still requires all policy-years and interactions, freezes FY2027–2036 baseline vintage, disallows accounting ownership duplicates and excludes debt service from a primary score. It never asserts an official agency score.
