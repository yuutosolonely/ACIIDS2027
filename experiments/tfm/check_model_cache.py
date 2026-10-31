"""Development-only equivalence/timing check for the package's built-weight cache."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TABPFN_DISABLE_TELEMETRY"] = "1"
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from tabpfn.model_loading import clear_built_model_cache
from cric_ed.benchmark import get_table
from cric_ed.conditional import Encoder, TabPFNModel, column_specs, folds_and_bases, score_column

torch.set_num_threads(3)
table = get_table("movies_1", "real", 0)
specs = column_specs(table.dirty, table.eligible)
encoder = Encoder(table.dirty, specs)
X = encoder.features(table.dirty)
folds, bases = folds_and_bases(len(table.dirty), 5, 512, 0)
model = TabPFNModel(ROOT / "checkpoints/TabPFN-v2-clf/tabpfn-v2-classifier.ckpt",
                    ROOT / "checkpoints/TabPFN-v2-reg/tabpfn-v2-regressor.ckpt", seed=0, threads=3)
tasks = [(j, fold) for kind in ("numeric", "categorical")
         for j in [next(i for i, s in enumerate(specs) if s.kind == kind)] for fold in (0, 1, 0)]
results, seconds = {}, {}
with threadpool_limits(limits=3):
    for cache in (0, 2):
        os.environ["TABPFN_MODEL_CACHE_SIZE"] = str(cache)
        clear_built_model_cache()
        values, times = [], []
        for j, fold in tasks:
            keep = np.arange(len(specs)) != j
            t0 = time.perf_counter()
            values.append(score_column(model, specs[j], j, X[bases[fold]][:, keep],
                table.dirty[specs[j].name].values[bases[fold]], X[folds[fold]][:, keep],
                table.dirty[specs[j].name].values[folds[fold]], encoder.categorical_idx(j)))
            times.append(time.perf_counter() - t0)
        results[cache], seconds[cache] = values, times
diffs = [float(np.max(np.abs(a - b))) for a, b in zip(results[0], results[2])]
record = {"role": "development runtime optimization check; not detector performance evidence",
          "table": "movies_1", "seed": 0, "threads": 3, "cache_sizes": [0, 2],
          "tasks": tasks, "seconds_per_task": seconds, "max_abs_score_difference": diffs,
          "exact_equal": all(np.array_equal(a, b) for a, b in zip(results[0], results[2])),
          "status": "PASS" if all(d <= 1e-10 for d in diffs) else "FAIL",
          "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
out = ROOT / "experiments/validation/model_cache_equivalence_20261030.json"
if out.exists():
    raise FileExistsError(out)
out.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
if record["status"] != "PASS":
    raise SystemExit(1)
