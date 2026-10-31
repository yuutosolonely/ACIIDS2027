"""Fetch the public Springer template; never sends local manuscript contents."""
import hashlib
import io
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

URL = ("https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/"
       "content/27851904/data/LaTeX2e%20Proceedings%20Template%20ZIP")
out = Path(__file__).resolve().parents[1] / "paper/template"
if out.exists():
    raise FileExistsError(out)
data = urllib.request.urlopen(URL, timeout=45).read()
archive = zipfile.ZipFile(io.BytesIO(data))
files = {Path(name).name: archive.read(name) for name in archive.namelist()
         if Path(name).name.lower() in {"llncs.cls", "splncs04.bst", "history.txt", "readme.txt", "readme.md"}}
if not {"llncs.cls", "splncs04.bst"} <= files.keys():
    raise ValueError("Official archive missing expected files")
out.mkdir()
for name, content in files.items():
    (out / name).write_bytes(content)
(out / "SOURCE.json").write_text(json.dumps({"url": URL,
    "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    "zip_sha256": hashlib.sha256(data).hexdigest(),
    "files_sha256": {name: hashlib.sha256(content).hexdigest() for name, content in files.items()},
    "scope": "Public official template; no manuscript upload; retain embedded license notices"}, indent=2) + "\n")
print("Downloaded public template:", ", ".join(files))
