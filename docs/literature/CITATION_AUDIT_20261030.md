# Citation audit — 2026-10-30

### Further closest-work search during frozen execution (04:30 UTC)

Four additional primary records were inspected; these extend literature interpretation,
not the frozen detector or experimental design:

- `papastergios2025wild`: two authors/title/workshop verified on the primary QDB2025 PDF,
  https://www.vldb.org/2025/Workshops/VLDB-Workshops-2025/QDB/QDB25_1.pdf.
  §§2–4 inspected: embeddings, corruption scenarios and clean-context intervention.
  Broad claims that dirty-context TFM behavior or cleaner context benefits are first
  studied here are disallowed. No headline performance number borrowed.
- `bertiequille2026prior`: Laure Berti-Equille, arXiv2604.25154v1, 28April2026;
  https://arxiv.org/html/2604.25154v1, §§3–4 inspected. Learned cleaning-policy
  sequencing for TFM data preparation differs from fixed per-target removal and
  cell-ranking evaluation. No claim to reproduce its RL policy or theoretical assertions.
- `ipas2026lucos`: four authors/title verified in arXiv2605.27254v1, 26May2026;
  https://arxiv.org/html/2605.27254v1, §3.1 and Fig1 inspected. Unsupervised representation
  and medoid selection followed by oracle annotation for supervised TFM contexts.
  Label-free selection itself is not a novel claim of CRIC-ED.
- `zaccaria2025cellgmm`: four authors/title verified in arXiv2409.07881v3, 13May2025;
  https://arxiv.org/html/2409.07881v3, §§1–2 including penalized detection/imputation.
  Numerical mixture populations, not heterogeneous categorical text. Cite inspected
  preprint version here, without asserting unverified final journal metadata.

Public search strings: `"TabPFN" "cell" "error detection" context`;
`"tabular foundation" "data cleaning" contamination`;
`"cellwise" "trimming" "conditional" outlier detection`;
`"TabPFN" "context selection" anomaly detection`. Search hits are leads, not proof of
support. Cell-TRICC and other uninspected hits are not cited as verified methods.

## V2.1 manuscript support check (Codex continuation)

Source scope is `paper/sections/{introduction,related_work,method,protocol,limitations}.tex`.
This supersedes unsupported comparisons in the older closest-work matrix, not its history.

- **TabPFN:** full primary article read at https://pmc.ncbi.nlm.nih.gov/articles/PMC11711098/,
  especially “Principled in-context learning”, regression distribution description and
  Methods “Foundation model abilities / Density estimation”. Supports pretrained
  classification/regression, no per-dataset weight update for ICL, and existing
  autoregressive feature-conditional density estimation. Does not establish our dirty-context
  performance. Nature direct/DOI access redirected to inaccessible login; PMC full text succeeded.
- **CDC:** https://proceedings.mlr.press/v238/jager24a/jager24a.pdf, §§3.1–3.3 and 4.1/4.3,
  inspected. Supports column prediction, conformal calibration and the evaluated clean-training,
  corrupted-inference setting. Older claims “LOO calibration” and “fails without clean split”
  are not supported as universal statements and must not appear in manuscript.
- **DDC:** https://arxiv.org/pdf/1601.07251 (v4), §4 eight-step algorithm and §8 software,
  inspected. Supports numerical cellwise detection via robust prediction/residuals, including
  deshrinkage; no support for labelling DDCcore as the full reference algorithm or asserting
  a universal leave-cell-out protocol. Publisher full text had failed; primary author preprint read.
- **TACTIC:** https://arxiv.org/html/2603.14171v1, §§2–3 and 4.2–4.3, inspected.
  Supports anomaly-specific pretraining, row-level scoring and explicit contaminated-context
  experiments. Broad context-contamination novelty is disallowed. No cross-task score comparison.
- **ZeroED:** https://arxiv.org/html/2504.05345v1, abstract and §§III-A–III-E inspected.
  Supports LLM-derived features/labels and detector training. Cite preprint only here;
  no verified venue, per-prompt latency or universal numerical-column weakness asserted.
- **Raha:** primary author-deposited accepted-manuscript record
  https://dspace.mit.edu/entities/publication/f19685bd-d937-4287-b6dc-0563809e1987,
  identity and system summary checked. PDF download returned 429; alternate author PDF
  locations failed. Manuscript uses only system identity; benchmark bytes/provenance are
  verified separately by local manifest, not inferred from the paper abstract.
- **Isolation Forest:** https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf,
  title/authors and §§2–4 inspected; primary university metadata verifies venue/pages/year/DOI.
  Supports original isolation algorithm identity, not the claim that our column-wise
  implementation reproduces the original multivariate evaluation.
- **LightGBM:** official NeurIPS record and linked PDF
  https://proceedings.neurips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html,
  title/eight authors/year/volume and model identity checked. Our hyperparameters are
  protocol choices, not source-reported recommendations.

Newly added BibTeX keys `liu2008isolation` and `ke2017lightgbm` were checked against
these primary records. Existing unused entries are not evidence of support merely
because their metadata is verified. No private manuscript was sent in web queries.

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


## Addendum 2026-10-31 (Claude) — sources added to or changed in the manuscript

Identity checks use primary records; "support" names the text actually read. Search snippets were not used as evidence.

| Key | Identity source (checked 2026-10-31) | Content read | Sentence supported in paper | Limits |
|---|---|---|---|---|
| `chen2025autotest` | Author PDF (Microsoft Research), ACM reference line: Proc. ACM Manag. Data 3(3) (SIGMOD), Art. 133, 27 pp., DOI 10.1145/3725396; Crossref via `verify_reference` VERIFIED | Abstract, §on architecture (offline corpus training, online detection) | Learns semantic-domain constraints from a table corpus offline; detects erroneous column values without per-table expert constraints | Experiments not re-checked; not run |
| `ahmadi2025matelda` | EDBT 2025 OpenProceedings PDF: pp. 364–376 (first page 364, 13 pp.), DOI 10.48786/edbt.2025.29 printed (DataCite DOI; Crossref API returns 404) | Abstract, introduction, baselines paragraph | Semi-supervised; folds cells of several tables by domain/quality similarity; labelling budget shared across tables | Not run |
| `qin2026lucario` | Crossref: title, Qin/Li/Merlo, Inf. Softw. Technol. 192, 108035 (Apr 2026), CC-BY; Polytechnique Montréal record 71729 | Authors' replication-package README (unsupervised per-column type/categorical/numeric/regex constraint inference; default 95% coverage). Publisher full text blocked (HTTP 403, then CAPTCHA in browser — not bypassed) | Only: targets unsupervised, lightweight detection of pattern anomalies and outliers (title-level) | Abstract and experiments NOT read; no metric or dataset claim made |
| `fibbi2026celltricc` | Crossref: title, 5 authors, J. Comput. Graph. Stat., online 21 Apr 2026, pp. 1–16, CC-BY | Authors' ICORS 2025 abstract (unitn.it): cellwise trimming as extra step in Stochastic EM for latent block models; count data (Poisson); trimmed ICL | Cellwise trimming has been built into model-based co-clustering | Journal full text blocked (403); paper sentence limited accordingly |
| `bertiequille2026prior` | arXiv 2604.25154 — v2 (17 Sep 2026) retitled "Model-Aware Data Cleaning for Tabular Foundation Models"; v1 "Prior-Aligned …" | v1 and v2 abstracts and v2 comments (v2 corrects the prior-alignment framing; name now L2C-TFM) | Updated to v2: learns RL policies that sequence cleaning operators for TFM-oriented data preparation. Name "L2C2" removed from paper | Full text not re-read |
| `tactic2026`, `ipas2026lucos`, `zeroed2025`, `zaccaria2025cellgmm` | arXiv API via `verify_reference`: VERIFIED (titles/authors unchanged) | Support as recorded in the 2026-10-30 audit above | Unchanged | — |
| `ning2026ttc` (added after Codex review B-3) | arXiv 2610.12005v1 (8 Oct 2026), 8 authors (Ning, Biloš, Wilson, Zhang, Rasul, Song, Schneider, Nevmyvaka) | Abstract verbatim; HTML §1–8 mostly verbatim (appendix tail and references not read) | Attention-guided row retrieval helps on some large tables but can fail (class-composition distortion, e.g. COMET_MC); context expansion gives no consistent gain; supervised prediction with labelled contexts | Appendix numbers not used; no corrupted-context study in the read text |
