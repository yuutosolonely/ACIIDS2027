"""Preserve local run attempts, including failures and interruptions."""
from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class RunAttempt:
    def __init__(self, directory: Path, request: dict):
        self.directory = directory
        self.record = {"status": "running", "stage": "created", "request": request,
                       "started_at": self.now()}
        self.write()

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    def write(self):
        pending = self.directory / "attempt.json.new"
        pending.write_text(json.dumps(self.record, indent=2) + "\n", encoding="utf-8")
        pending.replace(self.directory / "attempt.json")

    def phase(self, name: str):
        self.record["stage"] = name
        self.write()


@contextmanager
def run_attempt(output: Path, request: dict, required=()):
    """Reserve a fresh sibling partial directory; never reuse or remove old evidence.

    The caller supplies artifacts inside the directory. Only a successful block with
    all required files is finalized. A record of failure remains at the partial path.
    """
    output = output.resolve()
    partial = output.with_name(output.name + ".partial")
    if partial.parent != output.parent:
        raise ValueError("Attempt paths must share the declared output directory")
    if output.exists():
        raise FileExistsError("Run output already exists: " + str(output))
    partial.mkdir(parents=True, exist_ok=False)
    attempt = RunAttempt(partial, request)
    try:
        yield attempt
        attempt.phase("finalize")
        for rel in required:
            path = (partial / rel).resolve()
            if not path.is_relative_to(partial) or not path.is_file():
                raise ValueError("Required run artifact is absent: " + rel)
        attempt.record.update(status="completed", finished_at=attempt.now())
        attempt.write()
        partial.rename(output)
    except BaseException as exc:
        interrupted = isinstance(exc, (KeyboardInterrupt, SystemExit))
        attempt.record.update(status="interrupted" if interrupted else "failed",
                              finished_at=attempt.now(),
                              error={"type": type(exc).__name__, "message": str(exc)[:500]})
        try:
            attempt.write()
        except OSError as log_error:
            exc.add_note("Could not update attempt record: " + type(log_error).__name__)
        raise
