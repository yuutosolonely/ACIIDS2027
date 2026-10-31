"""Create a readable Markdown companion from the same LaTeX prose and verified BibTeX."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pypandoc
import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def group(text, start):
    if text[start] != "{":
        raise ValueError("Expected braced LaTeX argument")
    depth = 1
    for i in range(start + 1, len(text)):
        if text[i] == "{" and text[i-1] != "\\":
            depth += 1
        elif text[i] == "}" and text[i-1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start+1:i], i+1
    raise ValueError("Unclosed braced argument")


def expand(text):
    while "\\IfFileExists" in text:
        start = text.index("\\IfFileExists")
        file, next_pos = group(text, start + len("\\IfFileExists"))
        yes, next_pos = group(text, next_pos)
        no, next_pos = group(text, next_pos)
        text = text[:start] + (yes if (PAPER / file).exists() else no) + text[next_pos:]
    return re.sub(r"\\input\{([^}]+)\}", lambda m: expand((PAPER / (m[1] if m[1].endswith(".tex") else m[1]+".tex")).read_text(encoding="utf-8")), text)


source = expand((PAPER / "main.tex").read_text(encoding="utf-8"))
pandoc = pypandoc.get_pandoc_path()
command = [pandoc, "--from=latex", "--to=gfm+tex_math_dollars", "--standalone", "--citeproc",
           "--bibliography=" + str(PAPER / "references.bib"), "--resource-path=" + str(PAPER)]
result = subprocess.run(command, input=source, text=True, encoding="utf-8", capture_output=True, cwd=PAPER)
if result.returncode:
    raise RuntimeError(result.stderr)
output = PAPER / "MANUSCRIPT.md"
front = re.match(r"\A---\n(.*?)\n---\n", result.stdout, re.S)
if front:
    metadata = yaml.safe_load(front[1])
    body = result.stdout[front.end():]
    rendered = "# " + metadata["title"] + "\n\n" + ", ".join(metadata.get("author", []))
    rendered += "\n\n## Abstract\n\n" + metadata.get("abstract", "") + "\n\n" + body
else:
    rendered = result.stdout
output.write_text("> Pre-submission manuscript awaiting author verification. Markdown companion generated from the LaTeX sources; the PDF controls layout. Empirical status follows the text below.\n\n" + rendered,
                  encoding="utf-8", newline="\n")
record = {"pandoc_version": subprocess.check_output([pandoc, "--version"], text=True).splitlines()[0],
          "expanded_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
          "markdown_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
          "warnings": result.stderr, "citation_style": "Pandoc default author-date; same BibTeX identities as PDF"}
(PAPER / "output/manuscript_provenance.json").write_text(json.dumps(record, indent=2) + "\n")
print("Updated English Markdown companion from LaTeX; citation/layout conversion warnings recorded")
