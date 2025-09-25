from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import argparse
import json
import os
import re
import requests
import sys
import time

BASE = 'https://search.mlp.cz'
LIST_URL = f'{BASE}/cz/davka/e-knihy_volne_ke_stazeni/'

DETAIL_RE = re.compile(r"/cz/titul/.+?/(?P<id>\d+)/?")
# GET_RE = re.compile(r"/cz/vypujcka/(?P<id>\d+)/?")

MARC_URL = "https://web2.mlp.cz/marc/marc.php?key={id}"

TAG_LINE_RE = re.compile(r'(^|[^0-9])(\d{3})(\s|$)')
SUBFIELD_RE = re.compile(r'(?:\||\u2021|‡|\$)\s*([0-9a-z])\s*(.+)', re.I)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

def fetch(url: str, params=None, retries: int = 3, pause = 0.5) -> str:
    """Gets HTML"""
    for i in range(retries):
        r = requests.get(url, params=params, headers=HEADERS, timeout=20)
        if r.ok:
            return r.text
        time.sleep(pause)
    r.raise_for_status()


def parse_list_page(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = {}

    for a in soup.find_all("a", href=DETAIL_RE):
        m = DETAIL_RE.search(a["href"])
        if not m: 
            continue
        
        if a["title"].lower() == "více":
            continue
        
        _id = m.group("id")
        items.setdefault(_id, {})
        items[_id]["id"] = _id
        items[_id]["detail_url"] = a["href"]
        items[_id]["title"] = a["title"]

    return list(items.values())


def fetch_marc_tokens(id: str) -> List[str] | None:
    """Stáhne marc.php a vrátí sekvenci tokenů (stripped_strings)."""
    url = MARC_URL.format(id=id)
    r = requests.get(url, headers=HEADERS, timeout=20)
    if not r.encoding or r.encoding.lower() in ("iso-8859-1", "latin-1"):
        r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")
    tokens = [t.strip() for t in soup.stripped_strings if t and t.strip()]
    return tokens or None



TAG_LINE_RE = re.compile(r'^\s*\d{3}\s*$')
SUBFIELD_LINE_RE = re.compile(r'^(?:\||\u2021|‡|\$)\s*([0-9a-z])(?:\s+(.*))?$', re.I)

SUBFIELD_TOKEN_RE = re.compile(r'^(?:\||\u2021|‡|\$)\s*([0-9a-zA-Z])(?:\s+(.*))?$', re.I)

def parse_marc_tokens(tokens: List[str]) -> List[Dict]:
    """Prepares marc content for work."""
    rows: List[Dict] = []
    current = None
    pending_code = None

    def finish_current():
        nonlocal current
        if current:
            rows.append(current)
            current = None

    for tok in tokens:
        while tok and tok[0] in "*•·-—–":
            tok = tok[1:].lstrip()
        if not tok:
            continue

        if re.fullmatch(r'\d{3}', tok):
            finish_current()
            current = {"tag": tok, "sub": {}}
            pending_code = None
            continue

        m = SUBFIELD_TOKEN_RE.match(tok)
        if m and current:
            code, val = m.groups()
            code = code.lower()
            if val and val.strip():
                if code in current["sub"]:
                    current["sub"][code] += " ; " + val.strip()
                else:
                    current["sub"][code] = val.strip()
                pending_code = None
            else:
                pending_code = code
            continue

        if current and pending_code:
            if pending_code in current["sub"]:
                current["sub"][pending_code] += " " + tok
            else:
                current["sub"][pending_code] = tok
            continue

        if current and current["sub"]:
            last_key = next(reversed(current["sub"]))
            current["sub"][last_key] = (current["sub"][last_key] + " " + tok).strip()

    finish_current()
    return rows



def extract_from_marc(id: str) -> Dict:
    """"""
    tokens = fetch_marc_tokens(id)

    if not tokens:
        return {"id": id, "author": None, "title": None, "downloads": []}

    rows = parse_marc_tokens(tokens)

    author = None
    for tag in ("100", "110", "111", "700"):
        for r in rows:
            if r["tag"] == tag and "a" in r["sub"]:
                author = r["sub"]["a"]
                break
        if author:
            break

    title_a = title_b = None
    for r in rows:
        if r["tag"] == "245":
            title_a = r["sub"].get("a")
            title_b = r["sub"].get("b")
            break
    title = (title_a or "") + ((" " + title_b.strip(" /:;")) if title_b else "")
    title = title.strip() or None

    downloads = []
    for r in rows:
        if r["tag"] == "856":
            u = r["sub"].get("u")
            q = r["sub"].get("q")
            if q:
                downloads.append({"format": q, "url": u})

    return {"id": id, "author": author, "title": title, "downloads": downloads}


def read_processed_ids_from_jsonl(path: str) -> set[str]:
    """Načte již uložené záznamy (podle 'id') z existujícího JSONL, aby šlo navázat (resume)."""
    ids = set()
    if not os.path.exists(path):
        return ids
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "id" in obj:
                    ids.add(str(obj["id"]))
            except Exception:
                continue
    return ids

def append_jsonl_record(path: str, record: dict):
    """Zapíše jeden řádek JSON: přidá do souboru, flush + fsync kvůli pádu."""
    line = json.dumps(record, ensure_ascii=False)

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def finalize_json_from_jsonl(jsonl_path: str, json_path: str):
    """Přečte JSONL a zapíše jako jedno pole do .json (volitelné)."""
    arr = []
    if not os.path.exists(jsonl_path):
        print(f"Varování: {jsonl_path} neexistuje, není co finalizovat.", file=sys.stderr)
        return
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                arr.append(json.loads(line))
            except Exception:
                continue
    with open(json_path, "w", encoding="utf-8") as out:
        json.dump(arr, out, ensure_ascii=False, indent=2)



def scrape_all(out_jsonl: str,
               limit: Optional[int] = None,
               sleep_between: float = 0.5,
               resume: bool = True,
               logger=print):
    """
    Projde stránkovaný seznam a KAŽDÝ záznam hned uloží do JSONL (append).
    Nepoužívá argparse ani __main__, vhodné pro Django BaseCommand.
    """
    processed = read_processed_ids_from_jsonl(out_jsonl) if resume else set()
    saved = 0
    offset = 0
    page_size = 20

    while True:
        html = fetch(LIST_URL, params={"offset": offset} if offset else None)
        page_items = parse_list_page(html)
        if not page_items:
            if logger: logger(f"Hotovo (offset={offset}): žádné další položky.")
            break

        for item in page_items:
            rec_id = str(item["id"])
            if resume and rec_id in processed:
                continue

            try:
                marc = extract_from_marc(rec_id)
            except Exception as e:
                if logger: logger(f"[WARN] extract_from_marc({rec_id}) selhalo: {e}")
                marc = {"id": rec_id, "author": None, "title": None, "downloads": []}

            record = {
                "id": rec_id,
                "title": item.get("title"),
                "author": marc.get("author"),
                "detail_url": item["detail_url"],
                "downloads": marc.get("downloads", []),
            }
            append_jsonl_record(out_jsonl, record)
            processed.add(rec_id)
            saved += 1
            if logger: logger(f"[OK] {rec_id} uloženo ({len(record['downloads'])} downloadů)")

            if limit and saved >= limit:
                if logger: logger(f"Dosažen limit {limit}, končím.")
                return

            time.sleep(sleep_between)

        offset += page_size
        if logger: logger(f"Další stránka (offset={offset})")


