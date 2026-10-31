TASK = prereg (task card T2). NAME = PREREG.

Owned files: prereg/PREREGISTRATION_V2_1.md (new), docs/handoffs/WT_PREREG_20261030.md.

Write the amended preregistration v2.1 from prereg/PREREGISTRATION_V2.md, the four accepted decisions and the amendment proposal where it is consistent with them. It must specify:
- research questions and estimands: primary = per real table, AUPRC(purify) - AUPRC(random) for TabPFN-2, mean over seeds; injected conditions are mechanism probes; secondary = TFM vs LGBM, oracle-clean gap, purify vs raw, leave-entity-out vs row-level, LGBM purify vs random;
- per-table descriptive reporting with 95% row-bootstrap intervals (same rows across seeds) and descriptive macro means; explicitly NO binary cross-dataset verdict and no Wilcoxon test over table x condition units, with the reason (conditions are not independent; see DES-01 in docs/CLAIM_EVIDENCE.md);
- data roles (development movies_1; confirmatory hospital, flights, beers, rayyan), 1,000-row cap and subsample rule, injection (10%, types, structures), the fact that injection seed = run seed;
- scoring semantics: negative log probabilities; numeric columns use a two-sided predictive tail probability, not a density; top-9 + OTHER; near-unique columns unsupported with score 0 and coverage reported;
- cross-fitting with K = 5 row folds, context cap 512, q = 0.15; arms raw, random, purify (nested pass-1 isolated from the outer fold), oracle (diagnostic), leaky (diagnostic, real only), raw_leo (secondary; keys hospital/provider_number, flights/flight, beers/brewery_id read from observed values; limitation stated);
- compute accounting: pass1_nested cost reported as purify's incremental cost; random scores do not depend on pass-1;
- models and pins (tabpfn 9.2.0, checkpoint manifest, n_estimators = 1, LightGBM 4.6.0 settings); the environment is not isolated (system site-packages inherited; provenance file experiments/validation/tfm_environment_provenance_20261030.json);
- failure and coverage-penalty policy;
- data-access disclosure: descriptive error profiles of all five tables were viewed on 2026-10-30; detectors have been run only on movies_1 and the synthetic fixture;
- deviation tables relative to v1 and to v2;
- freeze procedure: protocol hash plus full source manifest via REQUIRED_FREEZE_FILES in src/cric_ed/v2_contract.py.
Read src/cric_ed/conditional.py, benchmark.py, v2_contract.py, experiments/tfm/run_v2.py and analyze_v2.py to stay consistent with the code. Where code and decisions disagree, follow the decisions and list each discrepancy for the coordinator (the impl worker is changing that code in parallel). Do not reference any result. Status line: "CANDIDATE - becomes FROZEN only when its hash is recorded by the coordinator".
