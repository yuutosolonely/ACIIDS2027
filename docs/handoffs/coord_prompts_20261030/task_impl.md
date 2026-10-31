TASK = impl (task cards T1 and T3). NAME = IMPL.

Owned files: src/cric_ed/conditional.py, src/cric_ed/benchmark.py, src/cric_ed/baselines.py, src/cric_ed/v2_contract.py, src/cric_ed/run_record.py, experiments/tfm/** (run_v2.py, analyze_v2.py, README.md, new helper scripts, dev summaries), tests/test_v2_contract.py, tests/test_v2_cpu_boundaries.py, tests/test_run_record.py, new tests/test_v2_*.py, docs/handoffs/WT_IMPL_20261030.md.

T1. Review the coordinator's pre-directive edits (raw_leo arm with group folds, pass1_nested timing, ENTITY_KEYS/entity_groups, v2_contract pointing to prereg/PREREGISTRATION_V2_1.md and its .freeze.json/.sha256). Make decisions 1-4 of the decision brief executable. Rewrite the reporting in analyze_v2.py to per-table descriptive statistics:
- primary: tabpfn-v2__purify minus tabpfn-v2__random on each real table, seed-averaged, with a 95% row-bootstrap interval using the same resampled rows across seeds;
- mechanism probes: the same contrast per injected condition per table;
- secondary: TFM raw minus LGBM raw, oracle minus raw, purify minus raw, raw_leo minus raw (keyed tables, real condition), LGBM purify minus LGBM random;
- descriptive macro means across tables; a cost table including pass1_nested and per-arm seconds;
- remove the Wilcoxon/Holm verdicts; expect raw_leo arrays where defined;
- write CSV and LaTeX tables and figures into the analysis directory.
Fix all tests and add tests: group folds never put a query group into its own context; raw_leo argument validation; per-table analysis output on synthetic fake runs.
Acceptance for T1: `.venv-tfm/Scripts/python.exe -m pytest -q -p no:cacheprovider` passes; `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` passes (scientific modules may skip); `.venv/Scripts/python.exe tools/check_setup.py` reports PASS.

T3. Development run on movies_1 only: run_v2.py --table movies_1 --seeds 0 for each condition (real, inj-random, inj-systematic), both models, output to experiments/runs/v2_dev/ (gitignored is fine). Run the analysis code on these development artifacts into a scratch directory through an explicit --development flag that cannot be used for confirmatory tables. Record wall time per run and extrapolate the full confirmatory grid (4 tables x 3 conditions x 5 seeds, both models) on this 12-thread CPU, single process and with 3-4 parallel processes (state the thread setting). Report every failure. Save a small JSON summary (metrics and timings, no raw scores) to experiments/tfm/dev/dev_v2_1_movies.json.
