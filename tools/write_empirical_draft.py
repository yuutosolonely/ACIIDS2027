"""Prepare an evidence-bounded draft from the completed, audited frozen analysis.

This deterministic report does not certify novelty, visual layout, author review or acceptance.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
analysis_path = ROOT / "experiments/archive/v2_1_analysis/results.json"
audit_path = ROOT / "experiments/archive/v2_1_artifact_audit.json"
data = json.loads(analysis_path.read_text())
audit = json.loads(audit_path.read_text())
if data["role"] != "confirmatory" or audit["status"] != "PASS" or len(audit["runs"]) != 60:
    raise ValueError("Complete audited evidence required")
failures = sum(run.get("fit_failure_events", 0) for run in audit["runs"])
failure_text = (
    "with no recorded fit failures or final nonfinite predictions."
    if failures == 0
    else f"with {failures} caught fit-failure events (assigned maximal suspicion penalty per protocol) and zero fit failures on real-error conditions."
)
tables = ("hospital", "flights", "beers", "rayyan")
fmt = lambda x: f"{x:+.4f}"
effects = [data["units"][t+"|real"]["paired"]["purify_minus_random"] for t in tables]
macro = data["macro_descriptive"]["real|purify_minus_random"]["mean_delta"]
if data["macro_descriptive"]["real|purify_minus_random"]["n_tables"] != 4:
    raise ValueError("Primary table denominator")
effect_text = ", ".join(t + " $" + fmt(e["delta"]) + "$" for t, e in zip(tables, effects))
abstract = r"""Conditional prediction can score individual cells of a dirty table, but the
reference examples used by a tabular foundation model can themselves be corrupted.
We evaluate a fixed purification rule that removes rows with the largest nested
out-of-fold target-cell scores. All first-pass work is isolated from the outer query
fold. A paired random-removal control holds base contexts and removal counts fixed,
with nested preparation costs reported explicitly. The study comprises four capped
benchmark tables, real and two injected-error conditions, five seeds and both
TabPFN-2 and LightGBM. On real errors, the TabPFN purification-minus-random AP
differences are """ + effect_text + ". The equal-table descriptive mean is $" + fmt(macro) + r"""$.
These are per-table findings with conditional row-bootstrap uncertainty, not a
population-wide superiority verdict. We report support, rare-valid alarms,
boundary sensitivity and compute costs on the complete eligible-cell universe.
Final preprocessing is transductive, and repeated entities limit the interpretation
of row-bootstrap intervals. The evidence supports assessing context selection
against matched removal rather than assuming that a cleaner-looking context helps.
"""
results = r"""\section{Empirical Results}
\subsection{Completeness, support and primary comparison}
All 60 declared table--condition--seed units completed with both models. The saved
artifacts passed input, prediction and context-boundary checks, """ + failure_text + r"""
A separate flights/real/seed-0 rerun reproduced
every saved array and context record exactly; it is excluded from performance summaries.
This is same-implementation verification, not independent implementation replication.
Table~\ref{tab:coverage} shows the real-data universe and conditional support.
\input{generated/coverage}

The primary contrast compares purification with random removal on each real table,
averaging paired AP differences over all five seeds. The effects are """ + effect_text + r""".
Table~\ref{tab:primary} gives the APs and descriptive intervals. The unweighted
four-table mean is $""" + fmt(macro) + r"""$, without a macro significance test or confidence interval.
The intervals condition on saved predictions; they do not resolve dependence among
related rows or uncertainty across new source tables. Neither an interval excluding
zero nor a positive macro mean establishes general superiority.
\input{generated/primary}

\subsection{Comparators and information boundary}
Table~\ref{tab:baselines} reports measured baseline APs on the same complete eligible
universe. Frequency-based methods can score targets that the conditional pipeline
declares unsupported, while RobustZ and DDCcore have numerical support only. These
differences remain part of the deployment comparison and must not disappear through
successful-output-only evaluation. DDCcore and conditional LightGBM are separate
implementations, not reproduced DDC or CDC systems.
\input{generated/baselines}

Secondary differences in Table~\ref{tab:secondary} distinguish conditional-model,
oracle-context and observed-key boundary effects. The oracle changes context targets
and conditioning features together and retains the dirty-fitted encoder, so its gap
need not be positive and is not a theoretical upper bound. LEO uses different bases,
excludes observed keys only, and retains transductive final encoding. These contrasts
therefore diagnose sensitivity rather than isolate a single causal explanation.
\input{generated/secondary}

\subsection{Injection probes and rare-valid alarms}
Table~\ref{tab:probes} and Fig.~\ref{fig:mechanism} show the two injection conditions.
They remain separate from the real-error estimand: repeated wrong-value templates
and independently selected string corruptions need not resemble natural error
processes, and their seeds are coupled to context randomness. The saved analysis
also reports the derived systematic-minus-random oracle-gap difference descriptively,
without treating the conditions as independent datasets.
\input{generated/probes}
\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{generated/mechanism_deltas.pdf}
\caption{Injection-probe purification effects. Points are five-seed mean AP
differences, lines are descriptive 95\% row-bootstrap intervals. Conditions share
source tables and are not independent inferential units.}
\label{fig:mechanism}
\end{figure}

Table~\ref{tab:rare} reports rare-valid alarm fractions at the reference-error-count
budget, with the valid-cell denominator. This is an evaluation-only operating point.
An infrequent correct value is not defined as erroneous, and no rare-valid mask was
provided to purification. The complete seed-level export retains R-precision,
precision at 1\% and 5\%, type-specific AP, support and undefined-endpoint counts.
\input{generated/rare}

\subsection{Compute and scope of interpretation}
Table~\ref{tab:cost} separates nested preparation from final purification work.
The nested component is included in the inclusive purification time, and adding it
to ordinary random time produces the declared accounted matched-compute control
with unchanged random scores. It is not a separately timed accuracy arm. Wall times
come from concurrent local CPU execution; a temporary verification process also
shared the host. Peak memory and actual neural forward-call counts were not measured.
\input{generated/cost}

The appropriate conclusion concerns this fixed removal rule, pretrained weights,
support policy and capped collection. The real-error contrasts and injection probes
must be read together with baseline performance and rare-valid alarms. They do not
establish that context purification generally succeeds, that clean contexts always
help, or that an equal budget could not be better spent on another context strategy.
No outcome was used to revise the frozen design or select a subset of seeds.
"""
conclusion = r"""\section{Conclusion}
We evaluated a simple context-purification intervention for conditional cell-error
scoring under an explicitly transductive row-level protocol. On the four named
real-error tables, its paired AP differences to random removal were """ + effect_text + r""".
Nested isolation, complete denominators and explicit preparation cost are necessary
to interpret these results, but do not provide a robustness theorem or an independent
cross-dataset superiority claim. The retained predictions, context logs and frozen
analysis permit scrutiny of accuracy, support, rare-valid alarms and boundary
sensitivity. Broader claims require additional datasets, context strategies and
dependence-aware validation beyond this study.
"""
sections = ROOT / "paper/sections"
for name, content in (("abstract.tex", abstract), ("results.tex", results), ("conclusion.tex", conclusion)):
    path = sections / name
    if path.exists():
        raise FileExistsError("Do not overwrite an existing empirical section: " + str(path))
    path.write_text(content, encoding="utf-8", newline="\n")
(ROOT / "paper/output/empirical_draft_provenance.json").write_text(json.dumps({
    "status": "INTERNAL_DRAFT_REQUIRES_NUMERICAL_INTERPRETIVE_AND_VISUAL_REVIEW",
    "analysis_sha256": hashlib.sha256(analysis_path.read_bytes()).hexdigest(),
    "audit_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "primary_effects": {t: e for t, e in zip(tables, effects)}}, indent=2) + "\n")
print("Prepared evidence-bounded empirical draft; human/agent final review still required")
