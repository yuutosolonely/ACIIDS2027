# ACIIDS 2027 & Springer Publication Compliance Audit

**Worker:** W2-CONF (Conference & Reproducibility Specialist)  
**Worktree:** `C:/Users/ngoda/orca/workspaces/ACIIDS2027/conference`  
**Date of Verification:** 2026-10-29  
**Target Venue:** 19th Asian Conference on Intelligent Information and Database Systems (ACIIDS 2027)  
**Host City & Dates:** Bali, Indonesia, 5–7 April 2027  
**Official Portal:** https://aciids.pwr.edu.pl/2027/  

---

## 1. Official Conference Milestones & Strict Timelines

| Milestone | Official Deadline (AoE) | Vietnam/ICT Local Time (UTC+7) | Verification Status & Primary URL |
| :--- | :--- | :--- | :--- |
| **Full Paper Submission (Extended)** | **31 October 2026, 23:59 AoE** | **01 November 2026, 18:59 ICT** | **VERIFIED** — [dates.html](https://aciids.pwr.edu.pl/2027/dates.html), [submit.html](https://aciids.pwr.edu.pl/2027/submit.html) |
| **Notification of Acceptance** | Provisional January 2027 | Provisional January 2027 | Subject to IPC schedule updates |
| **Camera-Ready & Author Registration** | Provisional February 2027 | Provisional February 2027 | Mandatory at least 1 author registration |
| **Conference Event** | 5–7 April 2027 | 5–7 April 2027 | In-person presentation required for proceedings indexation |

> [!IMPORTANT]
> Time remaining from current session (2026-10-29 evening ICT): **~70 hours**.
> Confirmatory experiments and drafting must strictly respect this hard temporal ceiling.

---

## 2. Proceedings, Track Fit & Formatting Constraints

### Proceedings & Series
- **Publisher Series:** Springer Lecture Notes in Artificial Intelligence (LNAI) / Lecture Notes in Computer Science (LNCS).
- **Indexing:** SCOPUS, EI, ISI, ACM Digital Library.
- **Submission System:** EasyChair (`https://easychair.org/conferences/?conf=aciids2027`).

### Length & Style Guidelines
- **Template:** Springer LNCS LaTeX template (`llncs.cls`) or Word template. LaTeX is strongly recommended for mathematical precision and reproducibility.
- **Page Limits:**
  - Standard Full Paper: **12–15 pages** (strictly inclusive of abstract, tables, figures, bibliography, and appendix).
  - Absolute Cap: Up to 25 pages permitted only with approved extra-page surcharges.
  - Recommended Target for CRIC-ED: **13–14 pages** to avoid any layout overflow risk.

### Track & Special Session Alignment
1. **Regular Tracks:**
   - *Intelligent Information Systems & Database Systems*: Data cleaning, tabular representations, data quality auditing.
2. **Special Sessions:**
   - **DADIT (Data Analysis, Data Quality, Intelligent Information)**: Primary candidate session for cell error detection under heterogeneous tabular structures.
   - **ADMTA (Advanced Data Management and Analytics)**: Strong secondary candidate.

---

## 3. Publisher AI Disclosure & Academic Integrity Rules

Source: *Springer Nature Book Publishing Policies — Section: Artificial Intelligence (AI) and Authorship*.

### Permissible AI Assistance
- **Allowed:** Assistive tooling for literature indexing, syntax validation, coding, data visualization scripts, drafting, and English grammatical refinement.
- **Human Oversight:** Human authors retain 100% intellectual, scientific, and legal responsibility for every numerical value, mathematical derivation, claim, citation, and factual assertion.
- **Mandatory Disclosure Statement:** All accepted papers must include a transparent section in the manuscript:
  > *"Disclosure of AI Assistance: The authors utilized AI-based coding and drafting assistants for exploratory literature mapping, test suite scaffolding, and grammatical refinement under human authorial supervision. All statistical calculations, benchmark evaluations, mathematical formulation, and critical decisions were verified and approved by the authors."*

### Strict Prohibitions
- **Authorship:** Generative AI tools (LLMs, agents) **CANNOT** be listed as an author or co-author.
- **Synthetic/Hallucinated Citations:** Fabricating DOIs, arXiv identifiers, authors, or venues is considered scientific fraud.
- **Generative AI Figures:** Springer Nature policy strictly prohibits unverified synthetic images. All charts, graphs, and system architectures must be generated via deterministic code (`matplotlib`, `seaborn`, `pgfplots`, `mermaid` rendered natively) from measured logs.

---

## 4. Anonymity & Submission Integrity Protocol

1. **Double-Blind vs Single-Blind:**
   - ACIIDS main submission page does not mandate double-blind review for all tracks, but peer-review standards in LNAI favor anonymized submissions.
   - **Protocol for CRIC-ED Draft:** Prepare the primary draft with anonymized institutional affiliations and placeholder repository links (`https://anonymous.4open.science/...`), ready for immediate toggle if requested by the EasyChair form.
2. **Submission Boundaries:**
   - Automated workers and AI coordinators are **STRICTLY PROHIBITED** from logging into EasyChair, transmitting manuscripts externally, or contacting conference chairs.
   - Human authors must perform the final review, copyright signature, and submission upload.

---

## 5. Pre-Submission Verification Checklist (G6 Readiness Gate)

- [ ] **Temporal Validity:** Final upload finalized prior to 31 October 2026 23:59 AoE.
- [ ] **Page Count Compliance:** Between 12 and 15 pages in `llncs` format without altering margins, line spacing, or font sizes.
- [ ] **Template Integrity:** Compiled via standard pdfLaTeX with `llncs.cls` and `splncs04.bst`.
- [ ] **Claim-Evidence Completeness:** Every numerical entry in Tables 1–3 traceable to a verifiable run JSON artifact in `experiments/runs/`.
- [ ] **Citation Authenticity:** 100% of references verified via Crossref, Semantic Scholar, or arXiv primary records.
- [ ] **AI Disclosure Included:** Springer Nature compliant disclosure placed in Acknowledgements or dedicated section.
- [ ] **Originality & Duplicate Submission:** No overlapping submission active at any other journal or conference.
