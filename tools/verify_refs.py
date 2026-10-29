"""Kiểm chứng tham khảo: mọi entry phải tồn tại thật (Crossref / arXiv / Semantic Scholar).

    python tools/verify_refs.py paper/refs.bib docs/refs.bib
    python tools/verify_refs.py --doi 10.1145/3292500.3330701 --title "Optuna: ..."
    python tools/verify_refs.py --arxiv 1706.03762
Mã thoát 1 nếu có NOT_FOUND / MISMATCH / ERROR. Chưa VERIFIED thì gắn [UNVERIFIED], không dùng làm luận cứ.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import litlib  # noqa: E402


def parse_bib(text: str) -> list[dict]:
    """Parser BibTeX tối giản: đủ cho title/doi/eprint/year/url, chịu được ngoặc lồng."""
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        if m.group(1).lower() in ("comment", "string", "preamble"):
            continue
        i, depth = m.end(), 1
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[m.end(): i - 1]
        fields = {}
        for f in re.finditer(r"(\w+)\s*=\s*", body):
            j = f.end()
            if j < len(body) and body[j] == "{":
                d, k = 1, j + 1
                while k < len(body) and d:
                    d += {"{": 1, "}": -1}.get(body[k], 0)
                    k += 1
                value = body[j + 1: k - 1]
            elif j < len(body) and body[j] == '"':
                k = body.index('"', j + 1)
                value = body[j + 1: k]
            else:
                value = re.match(r"[^,\n]*", body[j:]).group(0)
            fields.setdefault(f.group(1).lower(), re.sub(r"[{}]", "", " ".join(value.split())))
        entries.append({"key": m.group(2), **fields})
    return entries


def arxiv_of(entry: dict) -> str | None:
    if entry.get("eprint"):
        return entry["eprint"]
    m = re.search(r"arxiv\.org/abs/([\w.\-/]+)", entry.get("url", "") + " " + entry.get("journal", ""))
    if m:
        return m.group(1)
    m = re.search(r"arXiv[:\s]+(\d{4}\.\d{4,5})", entry.get("journal", "") + " " + entry.get("note", ""), re.I)
    return m.group(1) if m else None


def report(label: str, res: dict) -> bool:
    found = res.get("found") or {}
    ok = res["status"] == "VERIFIED"
    print(f"{'OK ' if ok else '!! '} {res['status']:10} {label}")
    if found:
        print(f"      → {found.get('title')} ({found.get('year')}) · {found.get('venue') or '-'} · via {res.get('via')}")
    if res.get("note"):
        print(f"      note: {res['note']}")
    return ok


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("bibfiles", nargs="*")
    parser.add_argument("--doi")
    parser.add_argument("--arxiv")
    parser.add_argument("--title")
    parser.add_argument("--year", type=int)
    parser.add_argument("--no-cache", action="store_true", help="bỏ qua kết quả đã cache, hỏi lại API")
    args = parser.parse_args()
    use_cache = not args.no_cache

    all_ok = True
    if args.doi or args.arxiv or args.title:
        all_ok = report(args.doi or args.arxiv or args.title,
                        litlib.verify(args.doi, args.arxiv, args.title, args.year, use_cache=use_cache))
    for bib in args.bibfiles:
        entries = parse_bib(Path(bib).read_text(encoding="utf-8"))
        print(f"== {bib}: {len(entries)} entry ==")
        for e in entries:
            year = int(e["year"]) if e.get("year", "").isdigit() else None
            res = litlib.verify(e.get("doi"), arxiv_of(e), e.get("title"), year, use_cache=use_cache)
            all_ok &= report(f"{e['key']}: {e.get('title', '(không có title)')[:90]}", res)
            time.sleep(1.0)  # lịch sự với API công khai
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
