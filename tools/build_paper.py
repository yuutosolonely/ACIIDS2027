"""Build the local LaTeX draft using the checked official template; no uploads."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper"
BUILD = ROOT / ".cache/paper_build/v2_1"
BUILD.mkdir(parents=True, exist_ok=True)
for name in ("main.tex", "references.bib"):
    shutil.copyfile(SOURCE / name, BUILD / name)
for folder in ("sections", "generated"):
    if (SOURCE / folder).exists():
        shutil.copytree(SOURCE / folder, BUILD / folder, dirs_exist_ok=True)
for name in ("llncs.cls", "splncs04.bst"):
    shutil.copyfile(SOURCE / "template" / name, BUILD / name)
completed = subprocess.run(["tectonic", "--only-cached", "--keep-logs", "--keep-intermediates", "main.tex"], cwd=BUILD)
if completed.returncode:
    raise SystemExit(completed.returncode)
dest = SOURCE / "output"
dest.mkdir(exist_ok=True)
shutil.copyfile(BUILD / "main.pdf", dest / "cric_ed_v2_1.pdf")
shutil.copyfile(BUILD / "main.log", dest / "build.log")
import fitz
pdf = fitz.open(dest / "cric_ed_v2_1.pdf")
record = {"pages": len(pdf), "pdf_sha256": hashlib.sha256((dest / "cric_ed_v2_1.pdf").read_bytes()).hexdigest(),
          "template": json.loads((SOURCE / "template/SOURCE.json").read_text()),
          "sources_sha256": {str(p.relative_to(SOURCE)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in SOURCE.rglob("*") if p.is_file() and p.suffix in {".tex", ".bib"} and "archive" not in p.parts},
          "compiler": "tectonic --only-cached --keep-logs --keep-intermediates main.tex"}
(dest / "build_provenance.json").write_text(json.dumps(record, indent=2) + "\n")
(dest / "extracted.txt").write_text("\n\n".join(page.get_text() for page in pdf), encoding="utf-8")
render = dest / "rendered"
render.mkdir(exist_ok=True)
for i, page in enumerate(pdf):
    page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(render / f"page_{i+1:02}.png")
print(f"Built {len(pdf)} pages at {dest / 'cric_ed_v2_1.pdf'}")
