"""Pinned local TFM capability check; synthetic software evidence, never a benchmark."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

for key in ("HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "HF_HUB_DISABLE_TELEMETRY", "DO_NOT_TRACK"):
    os.environ[key] = "1"
os.environ["WANDB_MODE"] = "offline"

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from cric_ed.run_record import run_attempt  # noqa: E402
from cric_ed.v2_contract import verify_environment  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    request = {"run_id": args.out.name, "data_role": "synthetic capability check",
               "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO).decode().strip(),
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    blocked = []
    def refuse_connect(sock, address):
        blocked.append(str(address))
        raise RuntimeError("Network connection disabled for local capability validation")
    socket.socket.connect = refuse_connect
    socket.socket.connect_ex = refuse_connect
    with run_attempt(args.out, request, required=("capability.json",)) as attempt:
        attempt.phase("verify_environment")
        versions = verify_environment(REPO)
        manifest = json.loads((REPO / "data/manifests/tabpfn_v2_checkpoints_20261030.json").read_text())
        for entry in manifest["files"].values():
            path = REPO / entry["path"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError("Pinned checkpoint/license mismatch")
        attempt.phase("imports")
        import numpy as np
        import torch
        from tabpfn import TabPFNClassifier, TabPFNRegressor
        torch.set_num_threads(4)
        rng = np.random.default_rng(20261030)
        n, m, d = 64, 8, 3
        X = rng.normal(size=(n + m, d))
        y = 2 * X[:, 0] + X[:, 1] ** 2 + rng.normal(0, 0.2, n + m)
        result = {**request, "runtime_versions": versions, "torch_build": torch.__version__,
                  "device": "cpu", "threads": 4, "n_context": n, "n_query": m,
                  "features": d, "seed": 20261030, "checks": {}, "timing_sec": {}}
        attempt.phase("regression")
        start = time.perf_counter()
        reg = TabPFNRegressor(model_path=str(REPO / "checkpoints/TabPFN-v2-reg/tabpfn-v2-regressor.ckpt"),
                               device="cpu", n_estimators=1, random_state=0)
        reg.fit(X[:n], y[:n])
        full = reg.predict(X[n:], output_type="full")
        observed = torch.as_tensor(y[n:], dtype=full["logits"].dtype).unsqueeze(-1)
        cdf = full["criterion"].cdf(full["logits"], observed).detach().numpy()
        assert cdf.shape == (m, 1) and np.isfinite(cdf).all() and ((0 <= cdf) & (cdf <= 1)).all()
        tail = 2 * np.minimum(cdf[:, 0], 1 - cdf[:, 0])
        assert tail.shape == (m,) and np.isfinite(tail).all()
        result["checks"]["regression_cdf_and_tail"] = True
        result["regression_logits_shape"] = list(full["logits"].shape)
        result["timing_sec"]["regression"] = time.perf_counter() - start
        attempt.phase("classification")
        start = time.perf_counter()
        labels = (X[:, 0] > 0).astype(int)
        clf = TabPFNClassifier(model_path=str(REPO / "checkpoints/TabPFN-v2-clf/tabpfn-v2-classifier.ckpt"),
                                device="cpu", n_estimators=1, random_state=0)
        clf.fit(X[:n], labels[:n])
        p = clf.predict_proba(X[n:])
        assert p.shape == (m, 2) and np.isfinite(p).all() and np.allclose(p.sum(1), 1, atol=1e-6)
        assert ((p >= 0) & (p <= 1)).all()
        result["checks"]["classification_probabilities"] = True
        result["timing_sec"]["classification"] = time.perf_counter() - start
        result["blocked_network_attempts"] = blocked
        if blocked:
            raise RuntimeError("Unexpected network attempt during offline capability check")
        result["checkpoint_manifest_sha256"] = hashlib.sha256(
            (REPO / "data/manifests/tabpfn_v2_checkpoints_20261030.json").read_bytes()).hexdigest()
        (attempt.directory / "capability.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": request["run_id"], "capability": "PASS", "checks": result["checks"],
                      "network_attempts": len(blocked), "data_role": request["data_role"]}))


if __name__ == "__main__":
    main()
