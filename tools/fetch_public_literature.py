"""Cache public primary texts for local attribution/overlap review; no draft uploads."""
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / ".cache/literature_primary"
out.mkdir(parents=True, exist_ok=True)
sources = {
    "qualitab.pdf": "https://www.vldb.org/2025/Workshops/VLDB-Workshops-2025/QDB/QDB25_1.pdf",
    "l2c2.pdf": "https://arxiv.org/pdf/2604.25154v1",
    "lucos.pdf": "https://arxiv.org/pdf/2605.27254v1",
    "cellgmm.pdf": "https://arxiv.org/pdf/2409.07881v3",
    "ddc.pdf": "https://arxiv.org/pdf/1601.07251v4",
    "cdc.pdf": "https://proceedings.mlr.press/v238/jager24a/jager24a.pdf",
    "tactic.pdf": "https://arxiv.org/pdf/2603.14171v1",
    "zeroed.pdf": "https://arxiv.org/pdf/2504.05345v1",
    "tabpfn.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11711098/",
    "lightgbm.pdf": "https://proceedings.neurips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf",
    "iforest.pdf": "https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf",
}
records = []
for name, url in sources.items():
    p = out / name
    try:
        if not p.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "Research reference verification (public literature only)"})
            data = urllib.request.urlopen(request, timeout=40).read()
            if name.endswith(".pdf") and not data.startswith(b"%PDF"):
                raise ValueError("Expected a PDF, refusing to cache an error page")
            p.write_bytes(data)
        records.append({"file": name, "url": url, "status": "cached", "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    except Exception as exc:
        records.append({"file": name, "url": url, "status": "access_failed", "error": f"{type(exc).__name__}: {exc}"})
    print(name, records[-1]["status"], flush=True)
record = {"checked_utc": datetime.now(timezone.utc).isoformat(), "sources": records,
          "scope": "Public source texts cached locally; no manuscript or research data transmitted"}
(out / "manifest.json").write_text(json.dumps(record, indent=2) + "\n")
