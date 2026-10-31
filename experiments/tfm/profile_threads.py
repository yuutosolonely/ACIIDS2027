"""Development CPU timing on six fixed tasks; never tunes accuracy or research arms."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TABPFN_DISABLE_TELEMETRY"] = "1"
os.environ["TABPFN_MODEL_CACHE_SIZE"] = "0"
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from cric_ed.benchmark import get_table
from cric_ed.conditional import Encoder, TabPFNModel, column_specs, folds_and_bases, score_column

table = get_table("movies_1", "real", 0)
specs = column_specs(table.dirty, table.eligible)
encoder = Encoder(table.dirty, specs)
X = encoder.features(table.dirty)
folds, bases = folds_and_bases(len(table.dirty), 5, 512, 0)
tasks = [(next(i for i, s in enumerate(specs) if s.kind == kind), fold)
         for kind in ("numeric", "categorical") for fold in (0, 1, 0)]
results, timings = {}, {}
for threads in (1, 2, 3):
    torch.set_num_threads(threads)
    model = TabPFNModel(ROOT / "checkpoints/TabPFN-v2-clf/tabpfn-v2-classifier.ckpt",
                       ROOT / "checkpoints/TabPFN-v2-reg/tabpfn-v2-regressor.ckpt", seed=0, threads=threads)
    values, seconds = [], []
    with threadpool_limits(limits=threads):
        for j, fold in tasks:
            keep = np.arange(len(specs)) != j
            start = time.perf_counter()
            values.append(score_column(model, specs[j], j, X[bases[fold]][:, keep],
                table.dirty[specs[j].name].values[bases[fold]], X[folds[fold]][:, keep],
                table.dirty[specs[j].name].values[folds[fold]], encoder.categorical_idx(j)))
            seconds.append(time.perf_counter() - start)
    results[threads], timings[threads] = values, seconds
record = {"role": "development CPU thread timing; not detector performance evidence",
          "table": "movies_1", "seed": 0, "tasks": tasks, "seconds_per_task": timings,
          "cache_size": 0, "max_abs_vs_3": {t: max(float(np.max(np.abs(a-b))) for a, b in zip(values, results[3]))
                                           for t, values in results.items()},
          "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
out = ROOT / "experiments/validation/thread_profile_20261030.json"
if out.exists():
    raise FileExistsError(out)
out.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
