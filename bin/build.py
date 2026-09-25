#!/usr/bin/env python3
"""Build the PDF CV and the GitHub profile README from the single data source.

Sources (edit these, nothing else):
    _data/cv.yml              positions, education, teaching, talks, ...
    _bibliography/papers.bib  publications

Usage (from the repository root):
    python bin/build.py cv                     # -> assets/pdf/cv.pdf
    python bin/build.py readme --out README.md # -> GitHub profile README
    python bin/build.py all  --out README.md

Requirements (all free):  pip install -r bin/requirements.txt
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CV_YML = ROOT / "_data" / "cv.yml"
BIB = ROOT / "_bibliography" / "papers.bib"
CV_DIR = ROOT / "cv"
PDF_OUT = ROOT / "assets" / "pdf" / "cv.pdf"
README_TEMPLATE = ROOT / "bin" / "readme.md.j2"

ME = "Saleh"  # surname that gets bolded in author lists

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


# ----------------------------------------------------------------------------- bib
def _latex_to_text(s: str) -> str:
    from pylatexenc.latex2text import LatexNodes2Text

    s = s.replace("$L^2$", "L²").replace("{$L^2$}", "L²")
    return LatexNodes2Text(math_mode="verbatim").latex_to_text(s).strip()


def parse_bib(path: Path) -> list[dict]:
    """Minimal BibTeX parser for our own, well-formed file (brace-delimited values)."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\A---\s*\n---\s*\n", "", text)  # Jekyll front matter
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        etype, key = m.group(1).lower(), m.group(2)
        i, depth = m.end(), 1
        start = i
        while depth and i < len(text):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[start : i - 1]
        fields, j = {}, 0
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            if fm.start() < j:
                continue
            name, k = fm.group(1).lower(), fm.end()
            if body[k] == "{":
                d, k0 = 1, k + 1
                k += 1
                while d:
                    d += {"{": 1, "}": -1}.get(body[k], 0)
                    k += 1
                val = body[k0 : k - 1]
            else:
                k2 = body.find(",", k)
                k2 = len(body) if k2 == -1 else k2
                val, k = body[k:k2].strip(), k2
            fields[name] = val
            j = k
        entries.append({"type": etype, "key": key, **fields})
    return entries


def _initials(given: str) -> str:
    parts = re.split(r"[\s\-]+", given.strip())
    return " ".join(p if p.endswith(".") and len(p) <= 3 else p[0] + "." for p in parts if p)


def format_authors(raw: str) -> list[dict]:
    out = []
    for a in re.split(r"\s+and\s+", raw):
        a = _latex_to_text(a)
        if "," in a:
            last, given = [x.strip() for x in a.split(",", 1)]
        else:
            *g, last = a.split()
            given = " ".join(g)
        out.append({"name": f"{_initials(given)} {last}".strip(), "me": last == ME})
    return out


def publication(e: dict) -> dict:
    venue = e.get("journal") or e.get("booktitle") or e.get("school") or ""
    p = {
        "key": e["key"],
        "type": e["type"],
        "title": _latex_to_text(e.get("title", "")),
        "authors": format_authors(e.get("author", "")),
        "venue": _latex_to_text(venue),
        "volume": e.get("volume", ""),
        "number": e.get("number", ""),
        "pages": e.get("pages", "").replace("--", "–"),
        "year": int(e.get("year", 0)),
        "doi": e.get("doi", ""),
        "arxiv": e.get("arxiv", ""),
        "primaryclass": e.get("primaryclass", ""),
        "url": e.get("html") or e.get("pdf") or "",
        "code": e.get("code", ""),
        "selected": e.get("selected", "").lower() == "true",
        "section": e.get("cvsection", "peer-reviewed"),
    }
    if p["type"] == "phdthesis":
        p["venue"] = f"Dissertation, {p['venue']}"
    p["link"] = (
        f"https://doi.org/{p['doi']}" if p["doi"]
        else p["url"] or (f"https://arxiv.org/abs/{p['arxiv']}" if p["arxiv"] else "")
    )
    return p


def load_publications() -> list[dict]:
    pubs = [publication(e) for e in parse_bib(BIB)]
    # stable: newest first; within a year keep file order
    return sorted(pubs, key=lambda p: -p["year"])


# ----------------------------------------------------------------------------- cv.yml
def _date_key(d) -> str:
    return str(d or "9999")


def fmt_date(d) -> str:
    if d in (None, ""):
        return ""
    s = str(d)
    if re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", s):
        return f"{s[5:7]}/{s[:4]}"
    return s


def fmt_range(start, end) -> str:
    a, b = fmt_date(start), fmt_date(end)
    if not b:
        return f"since {a}"
    return f"{a} – {b}"


def visible(item: dict, target: str) -> bool:
    return target not in (item.get("hide_in") or [])


def load_cv(target: str) -> dict:
    data = yaml.safe_load(CV_YML.read_text(encoding="utf-8"))

    def keep(items):
        return [i for i in (items or []) if visible(i, target)]

    for k in ("positions", "education", "students", "stays", "talks", "events", "software"):
        data[k] = keep(data.get(k))
    data["teaching"]["courses"] = keep(data["teaching"].get("courses"))
    for x in data["positions"] + data["education"] + data["stays"]:
        x["range"] = fmt_range(x.get("start"), x.get("end"))
    for t in data["talks"] + data["events"]:
        t["year"] = str(t["date"])[:4]
    data["talks"].sort(key=lambda t: _date_key(t["date"]), reverse=True)
    data["talks_by_type"] = {
        k: [t for t in data["talks"] if t["type"] == k]
        for k in ("invited", "contributed", "poster", "seminar")
    }
    return data


# ----------------------------------------------------------------------------- outputs
def build_cv() -> Path:
    import typst

    data = load_cv("cv")
    pubs = [p for p in load_publications() if visible(p, "cv")]
    data["publications"] = {
        "peer_reviewed": [p for p in pubs if p["section"] == "peer-reviewed"],
        "preprints": [p for p in pubs if p["section"] == "preprint"],
    }
    today = dt.date.today()
    data["updated"] = f"{MONTHS[today.month - 1]} {today.year}"

    build = CV_DIR / "build"
    build.mkdir(exist_ok=True)
    (build / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    typst.compile(
        str(CV_DIR / "cv.typ"),
        output=str(PDF_OUT),
        root=str(ROOT),
        font_paths=[str(CV_DIR / "fonts")],
    )
    print(f"CV     -> {PDF_OUT.relative_to(ROOT)}")
    return PDF_OUT


def build_readme(out: Path, template: Path = README_TEMPLATE) -> Path:
    import jinja2

    data = load_cv("readme")
    pubs = [p for p in load_publications() if visible(p, "readme") and p["section"] != "thesis"]
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template.parent)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )

    def authors_md(authors):
        return ", ".join(f"**{a['name']}**" if a["me"] else a["name"] for a in authors)

    env.filters["authors"] = authors_md
    text = env.get_template(template.name).render(
        cv=data,
        profile=data["profile"],
        selected=[p for p in pubs if p["selected"]],
        pubs=pubs,
        recent_talks=[t for t in data["talks"] if t["type"] != "seminar"][:5],
        n_talks=len([t for t in data["talks"] if t["type"] != "seminar"]),
        n_invited=len(data["talks_by_type"]["invited"]),
    )
    out.write_text(text, encoding="utf-8")
    print(f"README -> {out}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["cv", "readme", "all"])
    ap.add_argument("--out", type=Path, default=Path("README.md"), help="README output path")
    ap.add_argument("--template", type=Path, default=README_TEMPLATE)
    a = ap.parse_args(argv)
    if a.what in ("cv", "all"):
        build_cv()
    if a.what in ("readme", "all"):
        build_readme(a.out, a.template)
    return 0


if __name__ == "__main__":
    sys.exit(main())
