"""CLI tìm tài liệu (bản dự phòng khi MCP aciids-lab không chạy). Chạy từ thư mục gốc repo.

    python tools/lit.py search "LLM time series anomaly detection" --limit 10 --from 2023
    python tools/lit.py show DOI:10.18653/v1/2023.acl-long.1
    python tools/lit.py show ARXIV:2310.06625 --json

Kết quả tìm kiếm là đầu mối; paper nào đưa vào tài liệu phải qua tools/verify_refs.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import litlib  # noqa: E402


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--from", dest="year_from", type=int, default=2023)
    p.add_argument("--sources", default="s2,openalex,arxiv")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("show")
    p.add_argument("paper_id")
    p.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.cmd == "search":
        out = litlib.search(args.query, args.limit, args.year_from, tuple(args.sources.split(",")))
        if args.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
            return
        for i, r in enumerate(out["results"], 1):
            ident = f"DOI:{r['doi']}" if r.get("doi") else (f"ARXIV:{r['arxiv']}" if r.get("arxiv") else r.get("url", ""))
            print(f"{i:2}. [{r.get('year')}] {r['title']}")
            print(f"    {r.get('authors')} · {r.get('venue') or '-'} · cites={r.get('citations')} · {ident} · {'+'.join(r['sources'])}")
        for name, err in out["errors"].items():
            print(f"[cảnh báo] nguồn {name} lỗi: {err}")
    else:
        data = litlib.paper_details(args.paper_id)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return
        print(f"{data.get('title')} ({data.get('year')}) — {data.get('venue')}")
        print(", ".join(data.get("authors") or []))
        print(f"cites={data.get('citationCount')} refs={data.get('referenceCount')} ids={data.get('externalIds')}")
        if data.get("tldr"):
            print(f"TL;DR: {data['tldr']}")
        print()
        print(data.get("abstract") or "(không có abstract)")


if __name__ == "__main__":
    main()
