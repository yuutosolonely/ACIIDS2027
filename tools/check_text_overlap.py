"""Local exact-phrase screening against cached primary texts; not a plagiarism verdict."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ignore = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.ignore += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.ignore = max(0, self.ignore - 1)

    def handle_data(self, data):
        if not self.ignore:
            self.parts.append(data)


def tokens(text):
    text = unicodedata.normalize("NFKC", html.unescape(text))
    text = re.sub(r"([A-Za-z])-\s*\n\s*([A-Za-z])", r"\1\2", text)
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", text.lower())


def tex_body(text):
    text = re.sub(r"%[^\n]*", " ", text)
    text = re.sub(r"\\(?:cite|ref|label|url|input)\{[^}]*\}", " ", text)
    text = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", " ", text, flags=re.S)
    return re.sub(r"\\[A-Za-z]+\*?", " ", text).replace("{", " ").replace("}", " ")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--words", type=int, default=12)
    args = p.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    if args.words < 8:
        raise ValueError("Minimum phrase length eight words")
    cache = ROOT / ".cache/literature_primary"
    manifest = json.loads((cache / "manifest.json").read_text())
    source_grams = {}
    for entry in manifest["sources"]:
        if entry["status"] != "cached":
            continue
        file = cache / entry["file"]
        if hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("Cached source changed")
        if file.suffix == ".pdf":
            with pymupdf.open(file) as pdf:
                text = "\n".join(page.get_text() for page in pdf)
        else:
            parser = TextOnly()
            parser.feed(file.read_text(encoding="utf-8"))
            text = " ".join(parser.parts)
        words = tokens(text)
        source_grams[entry["file"]] = {tuple(words[i:i+args.words]) for i in range(len(words)-args.words+1)}
    manuscripts = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
                   for p in sorted((ROOT / "paper/sections").glob("*.tex"))}
    main = (ROOT / "paper/main.tex").read_text(encoding="utf-8")
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\keywords", main, re.S)
    if abstract:
        manuscripts["paper/main.tex:abstract"] = abstract.group(1)
    matches = []
    for name, text in manuscripts.items():
        words = tokens(tex_body(text))
        for i in range(len(words)-args.words+1):
            phrase = tuple(words[i:i+args.words])
            for source, grams in source_grams.items():
                if phrase in grams:
                    matches.append({"manuscript": name, "word_offset": i, "source": source,
                                    "matching_phrase": " ".join(phrase)})
    record = {"scope": f"Exact phrase screening on current prose and {len(source_grams)} cached primary texts; bibliography excluded",
              "limitations": "Does not detect semantic paraphrase or overlap with unsearched sources; not a plagiarism score or proof of originality",
              "phrase_words": args.words, "sources": manifest["sources"], "matches": matches,
              "manuscript_text_sha256": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in manuscripts.items()},
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Local screen: {len(matches)} exact {args.words}-word matches; manual attribution review still required")


if __name__ == "__main__":
    main()
