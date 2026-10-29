# Submission Readiness Report — Gate G6 Verification

**Worker:** W2-CONF (Conference Specialist) & Lead Research Coordinator  
**Worktree:** `C:/Users/ngoda/orca/workspaces/ACIIDS2027/conference`  
**Date:** 2026-10-29  
**Submission Portal:** EasyChair (ACIIDS 2027)  
**Final Submission Deadline:** **31 October 2026, 23:59 AoE (01 November 2026, 18:59 ICT)**  

---

## 1. Compliance Audit Matrix (Verified vs Unresolved)

| Requirement | Conference / Publisher Standard | Verification Evidence / Current State | Compliance Status |
| :--- | :--- | :--- | :--- |
| **Language** | English | Entire manuscript written in formal academic English (`paper/main.tex`, `paper/MANUSCRIPT.md`). | **VERIFIED** |
| **Format & Template** | Springer LNCS / LNAI style | Standard `llncs.cls` template structure used, `splncs04.bst` citations. | **VERIFIED** |
| **Page Length** | 12–15 pages full paper | Draft length: ~13 LNCS typeset pages including references. | **VERIFIED** |
| **Claim-Evidence Link** | 100% numerical traceability | Table 1 traces directly to `experiments/runs/run_pilot_001/metrics.json`. | **VERIFIED** |
| **Anonymity** | Anonymized for initial review | Author names and affiliations anonymized (`Anonymous Authors`). | **VERIFIED** |
| **AI Disclosure** | Springer Nature Risk-Based Policy | Transparent disclosure statement included in manuscript Section 6 / Acknowledgements. | **VERIFIED** |
| **Generative Images** | Springer restriction | Zero generative AI images; all results in code-generated LaTeX tables. | **VERIFIED** |
| **Originality & Novelty** | Original, unpublished | Novelty explicitly delimited to self-contamination & rare-valid preservation; prior work overlaps declared. | **VERIFIED** |

---

## 2. Unresolved Items Requiring Human Author Direction

1. **EasyChair Track / Special Session Selection:**
   - Public session calls confirm existence of **DADIT (Data Analysis, Data Quality, Intelligent Information)** and **ADMTA**.
   - Recommendation: Submit under DADIT as primary session, or Regular Track "Intelligent Information Systems".
2. **Author Names and Affiliations:**
   - Final author list and institutional details are held by the human author; must be entered in EasyChair author fields.
3. **External Submission Authorization:**
   - In accordance with `docs/AUTHORIZATION.md`, automated agents **DO NOT** have authorization to access EasyChair, create accounts, or upload manuscripts.
   - The final submission action belongs exclusively to the human researcher.

---

## 3. Package Manifest for Human Submission

The following files are verified, frozen, and ready for human submission packaging:
- **Manuscript Source:** `paper/main.tex`
- **Bibliography:** `paper/references.bib`
- **Readable Markdown Copy:** `paper/MANUSCRIPT.md`
- **Reproducibility Document:** `paper/REPRODUCIBILITY.md`
- **Audit Run Artifacts:** `experiments/runs/run_pilot_001/`
