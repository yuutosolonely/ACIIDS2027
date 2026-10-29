# Data Card & Benchmark Specifications — RAHA Candidates for CRIC-ED

**Worker:** W3-DATA (Data & Benchmark Specialist)  
**Worktree:** `C:/Users/ngoda/orca/workspaces/ACIIDS2027/data`  
**Date:** 2026-10-29  
**Status:** Protocol Frozen for Candidate Benchmarks; Synthetic Permitted Fixtures Configured.  

---

## 1. Candidate Benchmark Suite (RAHA Provenance)

Primary Upstream Source: https://github.com/BigDaMa/raha (Mahdavi & Abedjan, PVLDB 2020 / SIGMOD 2019).

| Dataset ID | Domain / Scope | Mixed Types (Num / Cat) | Natural / Injected Errors | Known Corruption Types | Rare-Valid Control Attributes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`beers`** | Commercial brewing data | 4 numeric, 7 categorical | Real-world dirty data | Typos in brewery names, swapped city/state, unit notation errors in ABV | Small craft breweries with unique ABV (<0.5% or >15%) |
| **`hospital`** | US Healthcare Provider directory | 3 numeric, 16 categorical | Real-world dirty records | Swapped hospital identifiers, corrupted ZIP codes, phone number permutations | Rural facilities with non-standard emergency service flags |
| **`flights`** | US Airline schedule records | 5 numeric, 9 categorical | Synthetic & real feed noise | Corrupted departure timestamps, invalid airport codes, flight duration swap | Rare cargo/seasonal carriers |
| **`rayyan`** | Medical publication citations | 2 numeric, 9 categorical / text | Manual curation errors | Truncated author initials, journal abbreviation inconsistencies | Rare specialized monographic publications |

---

## 2. Information Boundaries & Anti-Leakage Protocol

1. **Isolation of Ground-Truth Labels:**
   - Raw dirty table $\tilde{X}$ is stored in `data/benchmarks/<dataset>/dirty.csv`.
   - Clean reference table $X^*$ is stored in `data/benchmarks/<dataset>/clean.csv`.
   - Ground-truth binary error matrix $Y \in \{0, 1\}^{N \times D}$ ($1 = \text{error}, 0 = \text{clean}$) is stored in `data/benchmarks/<dataset>/errors.csv`.
   - **MANDATORY INVARIANT:** Detector algorithms **MUST NEVER** accept or read `clean.csv` or `errors.csv`. Only `src/cric_ed/evaluation/` is authorized to load error labels for metric calculation.
2. **Missing Values vs Erroneous Values:**
   - Missing indicators (`""`, `NaN`, `"null"`, `"None"`, `"?"`) are standardized into designated missing tokens during feature preprocessing.
   - If a cell is natively missing in the clean table, it is categorized as missing, not an error, unless declared as an erroneous null by the benchmark manifest.
3. **Grouped Cross-Fitting Boundaries:**
   - Where repeated entities exist (e.g. multiple beers from the same `brewery_id` or multiple records from the same `Provider Number`), rows sharing the entity ID form a unified cross-fitting block.
   - No row from entity cluster $E_k$ may be included in the context pool when evaluating query rows belonging to $E_k$.

---

## 3. Rare-Valid Control Subgroups

A critical hazard in cell error detection is **False Positive Inflation on Minority Patterns (Rare-Valid Cells)**:
- Values that are completely legitimate within the domain but occur with low frequency ($\le 1.0\%$ marginal frequency).
- For each benchmark dataset, the manifest identifies `rare_valid_columns` and flags rare valid patterns.
- Evaluation requires auditing the False Positive Rate (FPR) specifically on the rare-valid slice to verify that context trimming does not purge valid domain diversity.

---

## 4. Local Synthetic Fixture Policy ($0 Budget & Offline Compliance)

Under `docs/AUTHORIZATION.md`, downloading full external gigabyte datasets without verification is unauthorized.
To ensure immediate, reproducible, and offline test execution:
- Deterministic synthetic fixtures mimicking `beers` and `hospital` schemas are generated locally via `data/scripts/generate_fixtures.py`.
- Seed: `42`.
- Fixture size: 100 rows, 6 columns each, with controlled typo corruptions, swapped columns, and rare-valid controls.
