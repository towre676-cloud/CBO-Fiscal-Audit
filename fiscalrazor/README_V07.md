# FiscalRazor v0.7.0 — Primary Source Reconciliation Bridge

This release **retains the complete v0.6 legislative project** and adds an independently implemented source-calibration compatibility layer based on the other session's primary-source report. It **does not** claim that the other session's archive code was replayed or that the 18 original raw government CSVs are bundled. The evidence boundary is strict.

- 12 proposed legal provisions remain **unscored** (120 provision-year and 90 designated interaction-year empty template fields).
- 18 February 2026 CBO Git blob SHA-1s, with expected row counts totaling 97,459, are registered for reproducible acquisition.
- All 18 CBO Git blob SHA-1 identities and row counts were independently checked from source in this reconciliation in this reconciliation.
- A new eleven-year account-level summary reproduces CBO total and defense outlays directly from all 21,769 original-source rows read through the GitHub connector. The source parser rejects ambiguous duplicate date-variable keys and any SHA-1/row-count/schema mismatch.
- Six CY2036 CBO AGI-rank margins are reconstructed, with a **non-scoring mathematical lower bound** for a hypothetical AGI surtax.
- Original source archive admission remains at **zero**. Genuine national incidence and combined reform scores remain **NOT_ESTABLISHED**.

## Quick replay

```bash
python scripts/replay_all_v06.py
PYTHONPATH=src python -m unittest discover -s calibration/tests -v
python scripts/verify_cbo_original_v07.py --list
python scripts/verify_cbo_original_v07.py --require-complete  # expected to FAIL until downloaded
python scripts/verify_package.py
```

See `docs/LATEST_SESSION_RECONCILIATION_2026_11_06.md` and `results/v07/calibration_partial_identification.json` for mathematical and verification detail.
