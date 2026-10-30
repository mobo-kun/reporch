"""Read the user's raw material with the standard library only.

v1 formats: plain text and Markdown (notes, chat, voice transcripts), .vtt/.srt transcripts, .docx
(Word, Google Docs export), .csv/.tsv (Google Forms, Typeform, Sheets), .xlsx (Excel, Typeform).
Each file becomes {"kind", "text"} and, for spreadsheets, {"tables": [{"name", "rows"}]}.
"""
import csv
import io
import os
import re
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
TEXT_EXT = {".txt", ".md", ".markdown"}
SUPPORTED = TEXT_EXT | {".vtt", ".srt", ".docx", ".csv", ".tsv", ".xlsx"}
LATER = {".pdf": "PDF reports are migrated (migrate module)", ".html": "HTML reports are migrated (migrate module)",
         ".png": "images come in v2", ".jpg": "images come in v2", ".jpeg": "images come in v2",
         ".mp3": "audio comes in v2", ".m4a": "audio comes in v2", ".wav": "audio comes in v2",
         ".mp4": "video comes in v2", ".mov": "video comes in v2"}


def read(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXT:
        return {"kind": "text", "text": _read_text(path)}
    if ext in (".vtt", ".srt"):
        return {"kind": "transcript", "text": _subtitles(_read_text(path))}
    if ext == ".docx":
        return {"kind": "document", **_docx(path)}
    if ext in (".csv", ".tsv"):
        rows = _csv(path, "\t" if ext == ".tsv" else None)
        return {"kind": "table", "text": _rows_text(rows), "tables": [{"name": os.path.basename(path), "rows": rows}]}
    if ext == ".xlsx":
        tables = _xlsx(path)
        return {"kind": "table", "text": "\n\n".join(f"# {t['name']}\n{_rows_text(t['rows'])}" for t in tables),
                "tables": tables}
    raise ValueError(LATER.get(ext, f"{ext or 'this file type'} is not supported yet; export it as .docx, .csv, .xlsx or .txt"))


def _read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-16", "cp1256", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue


def _subtitles(text):
    out, last = [], None
    for line in text.splitlines():
        line = line.strip()
        if not line or line == "WEBVTT" or line.isdigit() or "-->" in line or line.startswith(("NOTE", "STYLE")):
            continue
        line = re.sub(r"<v\s+([^>]+)>", r"\1: ", line)
        line = re.sub(r"<[^>]+>", "", line)
        if line != last:
            out.append(line)
        last = line
    return "\n".join(out)


def _docx(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(f"{W}body")
    paras, tables = [], []

    def ptext(p):
        parts = []
        for el in p.iter():
            if el.tag == f"{W}t" and el.text:
                parts.append(el.text)
            elif el.tag in (f"{W}tab",):
                parts.append("\t")
            elif el.tag in (f"{W}br", f"{W}cr"):
                parts.append("\n")
        return "".join(parts)

    for el in body:
        if el.tag == f"{W}p":
            t = ptext(el)
            style = el.find(f"{W}pPr/{W}pStyle")
            if style is not None and style.get(f"{W}val", "").lower().startswith("heading") and t:
                t = "#" * min(6, int(re.sub(r"\D", "", style.get(f"{W}val")) or 1)) + " " + t
            paras.append(t)
        elif el.tag == f"{W}tbl":
            rows = [[ " ".join(ptext(p) for p in tc.iter(f"{W}p")).strip() for tc in tr.findall(f"{W}tc")]
                    for tr in el.findall(f"{W}tr")]
            tables.append({"name": f"table {len(tables) + 1}", "rows": rows})
            paras.append(_rows_text(rows))
    return {"text": "\n".join(paras).strip(), "tables": tables}


def _csv(path, delimiter=None):
    text = _read_text(path)
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text[:4096], delimiters=",;\t").delimiter
        except csv.Error:
            delimiter = ","
    return [row for row in csv.reader(io.StringIO(text), delimiter=delimiter)]


def _col(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def _xlsx(path):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(f"{S}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{S}t")))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target = {r.get("Id"): r.get("Target") for r in rels}
        tables = []
        for sh in wb.find(f"{S}sheets"):
            t = target[sh.get(f"{R}id")].lstrip("/")
            t = t if t.startswith("xl/") else "xl/" + t
            rows = []
            for row in ET.fromstring(z.read(t)).iter(f"{S}row"):
                cells = {}
                for c in row.findall(f"{S}c"):
                    kind, v = c.get("t"), c.find(f"{S}v")
                    if kind == "s" and v is not None:
                        val = shared[int(v.text)]
                    elif kind == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter(f"{S}t"))
                    else:
                        val = v.text if v is not None else ""
                    cells[_col(c.get("r"))] = val
                if cells:
                    rows.append([cells.get(i, "") for i in range(max(cells) + 1)])
            tables.append({"name": sh.get("name"), "rows": rows})
    return tables


def _rows_text(rows):
    return "\n".join(" | ".join(str(c) for c in r) for r in rows)
