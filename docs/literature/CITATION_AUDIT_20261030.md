# Citation audit — 2026-10-30

Identity = title/authors/venue/pages match a primary record. Support = the cited source's
own text (abstract or body actually read) supports the sentence in `paper/main.tex`.
Support marked UNVERIFIED was not checked against the full paper in this session.

| Key | Primary record checked (2026-10-30) | Identity | Errors fixed in `references.bib` | Claim in draft (pre-audit) | Support |
|---|---|---|---|---|---|
| `jager2024cdc` | PMLR v238 landing page (`proceedings.mlr.press/v238/jager24a.html`) | VERIFIED | Removed non-existent author "Wachinger, Christian"; pages 3160–3168 → 3394–3402 | "imputers followed by conformal residual calibration" | PARTIAL: abstract states imputation + conformal prediction. "Cell error detection", "assumes a clean calibration split" — UNVERIFIED |
| `hollmann2025tabpfn` | Crossref DOI 10.1038/s41586-024-08328-6 | VERIFIED | Removed "Franke", "Grabocka"; added Körfer, Hoo, Schirrmeister | TabPFN is a tabular foundation model | VERIFIED (title) |
| `rousseeuw2018ddc` | Crossref DOI 10.1080/00401706.2017.1340909 | VERIFIED | DOI added | robust numeric cellwise deviance baseline | UNVERIFIED beyond title |
| `raymaekers2024cellmcd` (was `rayyan2023cellmcd`) | Crossref DOI 10.1080/01621459.2023.2267777 | VERIFIED | vol 118(543) pp 2026–2037 → 119(548) pp 2610–2621; key renamed | cellwise robust estimator | UNVERIFIED beyond title |
| `mahdavi2019raha` (was `mahdavi2020raha`) | Crossref DOI 10.1145/3299869.3324956 | VERIFIED | Venue PVLDB 12(11) 1486–1499 → SIGMOD 2019 pp 865–882; 2 → 7 authors; key renamed | benchmark suite source | Datasets obtained from the authors' repository (Apache-2.0); see `data/manifests/raha_download_20261030.json` |
| `tactic2026` | arXiv abs 2603.14171 (v1, 2026-03-15) | VERIFIED | author `Anonymous` → Marszałek, Kuśmierczyk, Śmieja | in-context anomaly scoring with TabPFN; context instability; row score | PARTIAL: abstract states in-context models struggle with contaminated data for unsupervised AD; row-level scoring consistent with abstract |
| `zen2026focus` | arXiv abs 2610.06693 (v1, 2026-10-05) | VERIFIED | author `Anonymous` → Bershtman, Cohen | adapts PFNs for anomaly detection | PARTIAL: abstract (nearest-neighbour distances on frozen features; ADBench) |
| `ticda2026` | arXiv abs 2610.07996 (v1, 2026-10-06) | VERIFIED | author `Anonymous` → 7 authors | linear surrogates for context attribution; supervised labels | PARTIAL: abstract (linear surrogates on latent embeddings; labeling-error detection) |
| `zeroed2025` | arXiv abs 2504.05345 | VERIFIED (arXiv) | author `Anonymous` → 7 authors; ICDE venue removed | "LLM reasoning ... latency (>10 s per prompt)" | Venue ICDE 2025 UNVERIFIED; ">10 s per prompt" UNVERIFIED → removed from draft |

Access limits: ACM DL and DBLP returned 403/anti-bot pages; Nature redirected to a login wall,
so Crossref was used for those records.
