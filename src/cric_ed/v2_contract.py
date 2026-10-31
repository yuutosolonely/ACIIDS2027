"""Local validation for the candidate v2 pipeline; this module grants no authorization.

No freeze files are created here. A future freeze must cover protocol, execution and
analysis together. Synthetic tests of this contract are software evidence only.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import re
from pathlib import Path

TABLES = ("hospital", "flights", "beers", "rayyan")
CONDITIONS = ("real", "inj-random", "inj-systematic")
SEEDS = (0, 1, 2, 3, 4)
MODELS = ("tabpfn-v2", "lgbm")
BASELINES = ("VF", "PF", "RobustZ", "ColumnIF", "DDCcore")
SOURCE_FILES = (
    "src/cric_ed/conditional.py", "src/cric_ed/baselines.py",
    "src/cric_ed/benchmark.py", "src/cric_ed/v2_contract.py",
    "src/cric_ed/run_record.py",
    "experiments/tfm/run_v2.py", "experiments/tfm/analyze_v2.py",
)
PREREG = "prereg/PREREGISTRATION_V2_1.md"
REQUIRED_FREEZE_FILES = SOURCE_FILES + (
    PREREG, "experiments/tfm_env_freeze.txt",
    "data/manifests/raha_download_20261030.json",
    "data/manifests/tabpfn_v2_checkpoints_20261030.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze(root: Path) -> dict:
    """Reject missing/stale protocol or code locks; never write a lock implicitly."""
    root = root.resolve()
    lock = root / "prereg/PREREGISTRATION_V2_1.freeze.json"
    legacy = root / "prereg/PREREGISTRATION_V2_1.sha256"
    if not lock.is_file() or not legacy.is_file():
        raise ValueError("Candidate v2 is not frozen: protocol hash and full source manifest required")
    data = json.loads(lock.read_text(encoding="utf-8"))
    files = data.get("files_sha256")
    if data.get("schema_version") != 1 or not isinstance(files, dict):
        raise ValueError("Invalid v2 freeze manifest")
    missing = set(REQUIRED_FREEZE_FILES) - files.keys()
    if missing:
        raise ValueError("Freeze omits required files: " + ", ".join(sorted(missing)))
    for rel, digest in files.items():
        path = (root / rel).resolve()
        if not path.is_relative_to(root) or Path(rel).is_absolute():
            raise ValueError("Freeze path escapes repository: " + rel)
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid SHA-256 for " + rel)
        if not path.is_file() or sha256(path) != digest:
            raise ValueError("Frozen file differs or is absent: " + rel)
    text = legacy.read_text(encoding="utf-8").split()
    if not text or text[0] != files[PREREG]:
        raise ValueError("Protocol hash and full source freeze disagree")
    identity = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"prereg_sha256": files[PREREG], "source_snapshot_sha256": identity,
            "code_sha256": {p: files[p] for p in SOURCE_FILES}}


def validate_run_metadata(meta: dict, expected: dict) -> tuple[str, str, int]:
    """Validate identity before reading predictions; failures remain reportable data."""
    table, condition, seed = (meta.get(k) for k in ("table", "condition", "seed"))
    if table not in TABLES or condition not in CONDITIONS or type(seed) is not int or seed not in SEEDS:
        raise ValueError("Unexpected table, condition or seed")
    if meta.get("role") != "confirmatory":
        raise ValueError("Development artifacts cannot enter confirmatory analysis")
    if meta.get("status") != "completed":
        raise ValueError("Only completed runs may enter analysis")
    models = meta.get("models", [])
    if len(models) != len(MODELS) or set(models) != set(MODELS):
        raise ValueError("Both declared models are required exactly once")
    for key in ("prereg_sha256", "source_snapshot_sha256", "code_sha256"):
        if meta.get(key) != expected.get(key) or key not in expected:
            raise ValueError("Run does not match frozen " + key)
    if "checkpoint_sha256" in expected and meta.get("checkpoint_sha256") != expected["checkpoint_sha256"]:
        raise ValueError("Run does not match frozen checkpoint hashes")
    if not isinstance(meta.get("failures"), list):
        raise ValueError("Run must record its failures, including an empty list")
    return table, condition, seed


def checkpoint_hashes(root: Path) -> dict:
    """Read expected identities from the pinned manifest; no weight loading/downloads."""
    manifest = json.loads((root / "data/manifests/tabpfn_v2_checkpoints_20261030.json").read_text())
    found = {}
    for entry in manifest["files"].values():
        if entry["path"].endswith(".ckpt"):
            name = Path(entry["path"]).name
            key = {"tabpfn-v2-classifier.ckpt": "clf", "tabpfn-v2-regressor.ckpt": "reg"}.get(name)
            if key is None:
                raise ValueError("Unexpected checkpoint in pinned manifest")
            if key in found or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
                raise ValueError("Ambiguous or invalid checkpoint manifest")
            found[key] = entry["sha256"]
    if set(found) != {"clf", "reg"}:
        raise ValueError("Both pinned checkpoint identities are required")
    return found


def verify_local_inputs(root: Path, table: str) -> dict:
    """Verify frozen input bytes before running; no labels are given to a detector."""
    manifest = json.loads((root / "data/manifests/raha_download_20261030.json").read_text())
    for name in ("dirty.csv", "clean.csv"):
        rel = f"{table}/{name}"
        p = root / "data/raw/raha" / rel
        if rel not in manifest["sha256"] or not p.is_file() or sha256(p) != manifest["sha256"][rel]:
            raise ValueError("Dataset differs from pinned manifest: " + rel)
    model_manifest = json.loads((root / "data/manifests/tabpfn_v2_checkpoints_20261030.json").read_text())
    for entry in model_manifest["files"].values():
        rel = Path(entry["path"])
        # Dedicated worktrees intentionally mount the existing checkpoints read-only.
        # Validate the lexical manifest path, then verify every mounted file's bytes.
        if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] != "checkpoints":
            raise ValueError("Checkpoint path escapes repository")
        path = root / rel
        if not path.is_file() or sha256(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            raise ValueError("Checkpoint/license differs from pinned manifest: " + entry["path"])
    return checkpoint_hashes(root)


def validate_run_grid(identities: list[tuple[str, str, int]]) -> None:
    expected = {(t, c, s) for t in TABLES for c in CONDITIONS for s in SEEDS}
    observed = set(identities)
    if len(observed) != len(identities):
        raise ValueError("Duplicate table-condition-seed run")
    if observed != expected:
        raise ValueError(f"Incomplete or unexpected run grid: missing={len(expected - observed)}, "
                         f"unexpected={len(observed - expected)}")


def verify_environment(root: Path, lookup=None) -> dict:
    """Compare installed metadata with explicit pins, without importing a model."""
    if lookup is None:
        lookup = importlib.metadata.version
    normalize = lambda name: re.sub(r"[-_.]+", "-", name).lower()
    pins = {}
    for line in (root / "experiments/tfm_env_freeze.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^\s;]+)", line)
        if not match:
            raise ValueError("Environment record requires exact name==version pins")
        name, version = match.groups()
        key = normalize(name)
        if key in pins:
            raise ValueError("Duplicate environment pin: " + name)
        pins[key] = version
    core = {"torch", "tabpfn", "lightgbm", "numpy", "pandas", "scipy", "scikit-learn"}
    if core - pins.keys():
        raise ValueError("Environment record omits core distributions: " + ", ".join(sorted(core - pins.keys())))
    actual = {}
    errors = []
    for name, expected in pins.items():
        try:
            actual[name] = lookup(name)
        except importlib.metadata.PackageNotFoundError:
            errors.append(name + " is absent")
            continue
        if actual[name] != expected:
            errors.append(name + ": expected " + expected + ", found " + actual[name])
    if errors:
        raise ValueError("Runtime environment differs from pinned record: " + "; ".join(errors))
    return actual
