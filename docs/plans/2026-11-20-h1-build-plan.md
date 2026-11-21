# H1 Build Plan (2026-11-20)

Spec: `docs/plans/claude-code-build-brief.md`. This plan maps each part of the brief to a file and a check.

## Assumptions (decided, flag if wrong)

- **referral_source is always mapped** to "Source A", "Source B", … at import. The code can't tell whether a source name identifies a person, so it always plays safe. The mapping is consistent within a run, so routing still works.
- **Rows with an invalid DATE** (not a 4-digit year) are dropped at import and counted.
- **Extra safety beyond the brief:** `.gitignore` and the pre-commit check also block `*.tsv` and `*.xls`, since the brief allows a tab-separated export. `*.txt` is not blocked, because `requirements.txt` must be committed; tab-separated exports belong in `data/`, which is fully blocked.
- **"Looks like a name" in product_description** is a best-effort pattern: titles such as Dr./Mr./Mrs./Ms. followed by a name, and labels such as "patient:" or "name:". The by-eye check in `private-test-steps.md` is still required.
- **The optional local model reader (Ollama) is not built.** The brief marks it optional and off by default.
- **Baseline for products never seen in training:** no prediction, counted as a miss. The tool's backoff can still suggest a vendor for those.

## Layout and checks

| Step | Files | Done when |
|---|---|---|
| 1. Data guard | `.gitignore`, `scripts/check_no_data.py`, `.githooks/pre-commit` | Tests show data files are ignored and the hook rejects them |
| 2. Import | `h1/importer.py`, `h1/scrub.py` | Allowlist, identifier drop + warning (names only), pattern scrub, Expr1002 rule, year-only DATE, vendor/source mapping, xlsx + tab-separated, all tested |
| 3. Missing info | `h1/validate.py` | Each bad case flagged; blank diagnosis codes never flagged |
| 4. Suggestions | `h1/suggest.py` | Train 2024–2025 only; top 3 with plain-language reasons; backoff product → HCPCS + group → group |
| 5. Scoring | `h1/scoring.py`, `scripts/score.py` | Test on 2026 only; blank vendor rows excluded; baseline, per-group and multi-vendor results written to `output/` as counts only |
| 6. Coordinator screen | `app.py`, `.streamlit/config.toml` | Approve / Change vendor / Reject; decision + seconds logged to `logs/`; label "Local only · de-identified data"; usage stats off; bound to localhost |
| 7. Totals | `scripts/totals.py` | Prints only the four totals, baseline always shown |
| 8. Local-only guard | `tests/test_local_only.py` | Fails if any project code imports an HTTP client or AI SDK; the pipeline runs with network sockets disabled |
| 9. Verify | — | `pytest` passes; app starts on synthetic fixture data. **Real data is not loaded until Daniel says so.** |

Tests use abstract fixtures only (`PRODUCT_A`, `E0000`, `Vendor 01`), created at test time in a temp folder and never written to the repo.
