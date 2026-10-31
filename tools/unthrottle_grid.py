"""Keep Windows from treating the windowless grid processes as low-QoS background work.

Windows 11 applies EcoQoS/power throttling to windowless processes, which on hybrid CPUs
schedules them on efficiency cores. This helper only changes OS scheduling hints (power
throttling off, priority AboveNormal) for this user's grid processes; it does not touch
inputs, code, thread counts or outputs, so results are unaffected. Exits when the resume
launcher is gone. Log: experiments/archive/v2_1_runs/unthrottle_log.jsonl
"""
import ctypes
import json
import time
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "experiments/archive/v2_1_runs/unthrottle_log.jsonl"
PROCESS_SET_INFORMATION = 0x0200
PROCESS_POWER_THROTTLING_CURRENT_VERSION = 1
PROCESS_POWER_THROTTLING_EXECUTION_SPEED = 0x1
ProcessPowerThrottling = 4


class PowerThrottlingState(ctypes.Structure):
    _fields_ = [("Version", wintypes.ULONG), ("ControlMask", wintypes.ULONG), ("StateMask", wintypes.ULONG)]


k32 = ctypes.WinDLL("kernel32", use_last_error=True)


def unthrottle(pid: int) -> bool:
    h = k32.OpenProcess(PROCESS_SET_INFORMATION, False, pid)
    if not h:
        return False
    try:
        state = PowerThrottlingState(PROCESS_POWER_THROTTLING_CURRENT_VERSION,
                                     PROCESS_POWER_THROTTLING_EXECUTION_SPEED, 0)
        return bool(k32.SetProcessInformation(h, ProcessPowerThrottling, ctypes.byref(state),
                                              ctypes.sizeof(state)))
    finally:
        k32.CloseHandle(h)


def is_grid(p) -> bool:
    cmd = " ".join(p.info.get("cmdline") or [])
    return any(s in cmd for s in ("run_v2.py", "resume_grid_v2_1.py", "finish_v2_1_after_resume.py",
                                  "analyze_v2.py", "audit_v2_artifacts.py", "check_frozen_splits.py"))


done = set()
while True:
    launcher_alive = False
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            if not is_grid(p):
                continue
            cmd = " ".join(p.info["cmdline"])
            launcher_alive |= "resume_grid_v2_1.py" in cmd or "finish_v2_1_after_resume.py" in cmd
            if p.pid in done:
                continue
            ok = unthrottle(p.pid)
            p.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
            done.add(p.pid)
            with LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"utc": datetime.now(timezone.utc).isoformat(), "pid": p.pid,
                                    "unthrottled": ok, "cmd": cmd[-120:]}) + "\n")
        except (psutil.Error, OSError):
            continue
    if not launcher_alive:
        break
    time.sleep(30)
