TASK = lit (literature base for the manuscript). NAME = LIT.

Owned files: docs/literature/** (including CITATION_AUDIT_20261030.md, CLOSEST_WORK_MATRIX.md, papers.json, and a new RELATED_WORK_V2_1.md), docs/related-work.md, paper/references.bib, docs/handoffs/WT_LIT_20261030.md.

Goal: a verified related-work base for a CORE-B paper on unsupervised cell-level error detection with tabular foundation models under self-contamination. Cover:
- cell-level error detection systems and benchmarks (Raha, Baran, HoloClean/HoloDetect, ED2, Picket, dBoost, Auto-Detect/Uni-Detect, ZeroED and other LLM-based detectors);
- robust cellwise statistics (DDC, cellwise MCD) and imputation-based detection (CDC);
- tabular foundation models (TabPFN v2, TabICL) and their use for anomaly or outlier detection (TACTIC, ZEN, FoMo-0D, OutFormer, uTabPFN);
- in-context data attribution and curation (TICDA); learning with noisy or contaminated training data and trimmed estimators relevant to self-purification.
For every entry verify identity from a primary record (publisher or proceedings page, DOI via Crossref, arXiv abstract) and record the URL, access date, what you actually read (abstract or full text) and the exact statement it supports. Mark anything unverifiable as UNVERIFIED and keep it out of references.bib. Use `.venv/Scripts/python.exe tools/lit.py` and `tools/verify_refs.py` or your own web tools if available; record failures and access limits. Do not claim novelty; write a closest-work delta table stating what each work does and what remains open, with sources. Keep existing verified bib entries (change them only with evidence). All bib entries must render under splncs04 (use howpublished and url for arXiv preprints).
