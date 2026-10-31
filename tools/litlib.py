"""Tra cứu và kiểm chứng tài liệu học thuật qua API công khai.

Nguồn: Semantic Scholar, OpenAlex, arXiv (API + trang abs), DataCite, Crossref. Chỉ dùng thư viện chuẩn.
Dùng bởi tools/lit.py, tools/verify_refs.py và MCP aciids-lab (tools/mcp/research_lab.py) của repo này.
Nếu có biến môi trường S2_API_KEY thì gửi kèm để giảm lỗi 429 (không lưu khoá vào repo).
Kết quả verify được cache trong .cache/refcache/ tại gốc repo. Đây chỉ là kiểm metadata, không kiểm claim khoa học.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path

UA = "ACIIDS2027-TabFMED/0.3 (academic literature lookup)"
S2 = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "title,year,venue,authors,citationCount,externalIds,url"
ATOM = "{http://www.w3.org/2005/Atom}"


def _cache_base() -> Path:
    if os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"])
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")


CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache" / "refcache"
# Giãn nhịp tối thiểu giữa hai lần gọi cùng một máy chủ (arXiv yêu cầu ~3 giây).
MIN_INTERVAL = {"export.arxiv.org": 3.0, "arxiv.org": 1.0, "api.semanticscholar.org": 1.2}
_last_call: dict[str, float] = {}


def _throttle(host: str) -> None:
    wait = MIN_INTERVAL.get(host, 0.2) - (time.time() - _last_call.get(host, 0.0))
    if wait > 0:
        time.sleep(wait)
    _last_call[host] = time.time()


def _get(url: str, timeout: int = 25, retries: int = 4) -> bytes:
    headers = {"User-Agent": UA}
    if "semanticscholar" in url and os.environ.get("S2_API_KEY"):
        headers["x-api-key"] = os.environ["S2_API_KEY"]
    host = urllib.parse.urlparse(url).hostname or ""
    for attempt in range(retries + 1):
        _throttle(host)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise LookupError(url) from e
            if e.code in (429, 500, 502, 503) and attempt < retries:
                retry_after = e.headers.get("Retry-After", "") if e.headers else ""
                delay = float(retry_after) if retry_after.isdigit() else 2.0 * 2 ** attempt
                time.sleep(min(delay, 30) + random.uniform(0, 1))
                continue
            raise


def _json(url: str, retries: int = 4) -> dict:
    return json.loads(_get(url, retries=retries))


def norm_title(title: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (title or "").lower())).strip()


def similarity(a: str, b: str) -> float:
    return round(SequenceMatcher(None, norm_title(a), norm_title(b)).ratio(), 3)


def _authors(names: list[str]) -> str:
    return ", ".join(names[:3]) + (" et al." if len(names) > 3 else "")


# ------------------------------------------------------------------ search

def search_s2(query: str, limit: int, year_from: int | None) -> list[dict]:
    params = {"query": query, "limit": limit, "fields": S2_FIELDS}
    if year_from:
        params["year"] = f"{year_from}-"
    data = _json(f"{S2}/paper/search?{urllib.parse.urlencode(params)}")
    out = []
    for p in data.get("data", []):
        ext = p.get("externalIds") or {}
        out.append({
            "title": p.get("title"), "year": p.get("year"), "venue": p.get("venue") or "",
            "authors": _authors([a.get("name", "") for a in p.get("authors") or []]),
            "citations": p.get("citationCount"), "doi": ext.get("DOI"), "arxiv": ext.get("ArXiv"),
            "url": p.get("url"), "s2_id": p.get("paperId"),
        })
    return out


def search_openalex(query: str, limit: int, year_from: int | None, retries: int = 4) -> list[dict]:
    params = {"search": query, "per-page": limit}
    if year_from:
        params["filter"] = f"from_publication_date:{year_from}-01-01"
    data = _json(f"https://api.openalex.org/works?{urllib.parse.urlencode(params)}", retries=retries)
    out = []
    for w in data.get("results", []):
        source = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
        out.append({
            "title": w.get("display_name"), "year": w.get("publication_year"), "venue": source,
            "authors": _authors([(a.get("author") or {}).get("display_name", "") for a in w.get("authorships") or []]),
            "citations": w.get("cited_by_count"), "doi": doi, "arxiv": None, "url": w.get("id"),
        })
    return out


def _arxiv_entries(url: str) -> list[dict]:
    root = ET.fromstring(_get(url))
    out = []
    for e in root.findall(f"{ATOM}entry"):
        title = " ".join((e.findtext(f"{ATOM}title") or "").split())
        if not title or title.lower() == "error":
            continue
        aid = (e.findtext(f"{ATOM}id") or "").rsplit("/abs/", 1)[-1]
        out.append({
            "title": title, "year": int((e.findtext(f"{ATOM}published") or "0")[:4] or 0),
            "venue": "arXiv", "authors": _authors([a.findtext(f"{ATOM}name") or "" for a in e.findall(f"{ATOM}author")]),
            "citations": None, "doi": None, "arxiv": re.sub(r"v\d+$", "", aid), "url": f"https://arxiv.org/abs/{aid}",
        })
    return out


def search_arxiv(query: str, limit: int) -> list[dict]:
    params = {"search_query": f"all:{query}", "max_results": limit, "sortBy": "relevance"}
    return _arxiv_entries(f"https://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}")


def search(query: str, limit: int = 10, year_from: int | None = 2023,
           sources: tuple[str, ...] = ("s2", "openalex", "arxiv")) -> dict:
    """Tìm ở nhiều nguồn, gộp theo tiêu đề chuẩn hoá. Trả {results, errors}."""
    runners = {
        "s2": lambda: search_s2(query, limit, year_from),
        "openalex": lambda: search_openalex(query, limit, year_from),
        "arxiv": lambda: search_arxiv(query, limit),
    }
    merged: dict[str, dict] = {}
    errors = {}
    for name in sources:
        try:
            for rec in runners[name]():
                key = norm_title(rec["title"] or "")
                if not key:
                    continue
                cur = merged.setdefault(key, {**rec, "sources": []})
                cur["sources"].append(name)
                for field in ("doi", "arxiv", "venue", "citations", "year", "s2_id"):
                    if not cur.get(field) and rec.get(field):
                        cur[field] = rec[field]
        except Exception as e:  # nguồn lỗi không làm hỏng nguồn khác
            errors[name] = f"{type(e).__name__}: {e}"
    results = sorted(merged.values(), key=lambda r: (len(r["sources"]), r.get("citations") or 0), reverse=True)
    return {"results": results[: limit * 2], "errors": errors}


def paper_details(paper_id: str) -> dict:
    """paper_id: S2 id, 'DOI:10.x/y', 'ARXIV:2401.00001', hoặc URL."""
    fields = "title,abstract,year,venue,authors,citationCount,referenceCount,externalIds,tldr,url,publicationTypes"
    data = _json(f"{S2}/paper/{urllib.parse.quote(paper_id, safe=':/')}?fields={fields}")
    data["authors"] = [a.get("name") for a in data.get("authors") or []]
    data["tldr"] = (data.get("tldr") or {}).get("text")
    return data


# ------------------------------------------------------------------ verify

def datacite_doi(doi: str) -> dict | None:
    """DOI của arXiv (10.48550/...) và nhiều dataset đăng ký ở DataCite, không có trên Crossref."""
    try:
        attrs = _json(f"https://api.datacite.org/dois/{urllib.parse.quote(doi.lower())}")["data"]["attributes"]
    except LookupError:
        return None
    return {
        "title": ((attrs.get("titles") or [{}])[0]).get("title", ""), "year": attrs.get("publicationYear"),
        "venue": attrs.get("publisher") or "",
        "authors": _authors([c.get("name", "") for c in attrs.get("creators") or []]), "doi": doi,
    }


def crossref_doi(doi: str) -> tuple[dict | None, str]:
    """Crossref trước, DataCite nếu Crossref không có (DOI arXiv, dataset)."""
    if not doi.lower().startswith("10.48550/"):
        try:
            msg = _json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")["message"]
            year = ((msg.get("issued") or {}).get("date-parts") or [[None]])[0][0]
            return {
                "title": (msg.get("title") or [""])[0], "year": year,
                "venue": (msg.get("container-title") or [""])[0],
                "authors": _authors([a.get("family", "") for a in msg.get("author") or []]), "doi": doi,
            }, "crossref"
        except LookupError:
            pass
    return datacite_doi(doi), "datacite"


def _arxiv_abs_page(arxiv_id: str) -> dict | None:
    """Đọc thẻ citation_* trên trang https://arxiv.org/abs/<id> (dùng khi API export bị 429)."""
    try:
        page = _get(f"https://arxiv.org/abs/{urllib.parse.quote(arxiv_id)}").decode("utf-8", "replace")
    except LookupError:
        return None
    meta = {}
    for name, value in re.findall(r'<meta\s+name="(citation_[a-z_]+)"\s+content="([^"]*)"', page):
        meta.setdefault(name, []).append(html.unescape(value))
    if "citation_title" not in meta:
        return None
    date = (meta.get("citation_date") or meta.get("citation_online_date") or [""])[0]
    return {
        "title": meta["citation_title"][0], "year": int(date[:4]) if date[:4].isdigit() else None,
        "venue": "arXiv", "authors": _authors(meta.get("citation_author", [])),
        "arxiv": arxiv_id, "url": f"https://arxiv.org/abs/{arxiv_id}",
    }


def arxiv_record(arxiv_id: str) -> tuple[dict | None, str]:
    """API export → trang abs → DataCite (10.48550/arXiv.<id>). Trả (bản ghi, nguồn)."""
    arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
    try:
        entries = _arxiv_entries(f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(arxiv_id)}")
        if entries:
            return entries[0], "arxiv-api"
    except Exception:
        pass
    try:
        rec = _arxiv_abs_page(arxiv_id)
        if rec:
            return rec, "arxiv-abs"
    except Exception:
        pass
    rec = datacite_doi(f"10.48550/arXiv.{arxiv_id}")
    return rec, "datacite"


def _s2_match(title: str) -> list[dict]:
    data = _json(f"{S2}/paper/search/match?{urllib.parse.urlencode({'query': title, 'fields': S2_FIELDS})}",
                 retries=1)
    out = []
    for p in data.get("data") or []:
        ext = p.get("externalIds") or {}
        out.append({"title": p.get("title"), "year": p.get("year"), "venue": p.get("venue"),
                    "authors": _authors([a.get("name", "") for a in p.get("authors") or []]),
                    "doi": ext.get("DOI"), "arxiv": ext.get("ArXiv"), "url": p.get("url")})
    return out


def _arxiv_title_search(title: str) -> list[dict]:
    phrase = re.sub(r"[^\w\s-]", " ", title).strip()
    params = {"search_query": f'ti:"{phrase}"', "max_results": 3}
    return _arxiv_entries(f"https://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}")


def match_title(title: str) -> tuple[dict | None, str]:
    """Hỏi lần lượt S2 → OpenAlex → arXiv → Crossref; dừng khi có bản khớp ≥0.9, nếu không trả bản khớp nhất.

    Nhiều paper hội nghị ML (NeurIPS, ICLR…) không có DOI nên Crossref một mình không đủ.
    """
    best, best_src, best_score, answered = None, "", -1.0, False
    for source, finder in (("s2-match", lambda: _s2_match(title)),
                           ("openalex-match", lambda: search_openalex(title, 3, None, retries=2)),
                           ("arxiv-match", lambda: _arxiv_title_search(title)),
                           ("crossref-match", lambda: _crossref_search(title))):
        try:
            hits = finder()
        except Exception:
            continue  # nguồn đang 429/lỗi → nguồn kế tiếp
        answered = True
        for h in hits:
            score = similarity(title, h.get("title") or "")
            if score > best_score:
                best, best_src, best_score = h, source, score
        if best_score >= 0.9:
            break
    if not answered:
        raise RuntimeError("S2, OpenAlex, arXiv và Crossref đều không trả lời (thử lại sau vài phút)")
    return best, best_src


def _crossref_search(title: str) -> list[dict]:
    params = {"query.bibliographic": title, "rows": 3, "select": "DOI,title,issued,container-title,author"}
    items = _json(f"https://api.crossref.org/works?{urllib.parse.urlencode(params)}", retries=2)["message"]["items"]
    return [{
        "title": (it.get("title") or [""])[0],
        "year": ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0],
        "venue": (it.get("container-title") or [""])[0],
        "authors": _authors([a.get("family", "") for a in it.get("author") or []]), "doi": it.get("DOI"),
    } for it in items]


def _cache_path(doi: str | None, arxiv: str | None, title: str | None, year: int | None) -> Path:
    key = json.dumps([(doi or "").lower().strip(), (arxiv or "").lower().strip(), norm_title(title or ""), year])
    return CACHE_DIR / (hashlib.sha1(key.encode()).hexdigest() + ".json")


def verify(doi: str | None = None, arxiv: str | None = None, title: str | None = None,
           year: int | None = None, use_cache: bool = True) -> dict:
    """status: VERIFIED | MISMATCH | NOT_FOUND | ERROR. Kết quả không phải ERROR được cache."""
    cache = _cache_path(doi, arxiv, title, year)
    if use_cache and cache.exists():
        try:
            return {**json.loads(cache.read_text(encoding="utf-8")), "cached": True}
        except Exception:
            pass
    result = _verify(doi, arxiv, title, year)
    if result["status"] != "ERROR":
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            tmp = cache.with_suffix(f".{os.getpid()}.tmp")
            tmp.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
            tmp.replace(cache)
        except OSError:
            pass
    return result


def _verify(doi: str | None, arxiv: str | None, title: str | None, year: int | None) -> dict:
    try:
        if doi:
            found, via = crossref_doi(doi.strip())
        elif arxiv:
            found, via = arxiv_record(re.sub(r"^arxiv:", "", arxiv.strip(), flags=re.I))
        elif title:
            found, via = match_title(title)
        else:
            return {"status": "ERROR", "note": "Cần ít nhất doi, arxiv hoặc title."}
    except Exception as e:
        return {"status": "ERROR", "note": f"{type(e).__name__}: {e}"}
    if not found:
        return {"status": "NOT_FOUND", "via": via}
    title_based = via.endswith("-match")
    score = similarity(title, found.get("title") or "") if title else None
    threshold = 0.9 if title_based else 0.85
    status = "VERIFIED"
    notes = []
    if score is not None and score < threshold:
        status = "MISMATCH" if score >= 0.6 or not title_based else "NOT_FOUND"
        notes.append(f"tiêu đề lệch (score={score})")
    if year and found.get("year") and int(found["year"]) != int(year):
        status = "MISMATCH"
        notes.append(f"năm {year} ≠ {found['year']}")
    return {"status": status, "via": via, "score": score, "found": found, "note": "; ".join(notes)}
