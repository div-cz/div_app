from __future__ import annotations

import os
import json
import time
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from div_content.models import Booksource

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
}

#  nohup python manage.py scrape_missing_cbdb_books   --start-id 207198 --end-id 1000000   --output /div_app/div_app/cbdb_missing_03.jsonl   --delay 10 --resume --skip-jsonl   > /div_app/div_app/missing_cbdb_scraper.log 2>&1 &

def build_book_url(book_id: int) -> str:
    return f"https://cbdb.cz/kniha-{book_id}"

def parse_title_and_authors(soup: BeautifulSoup):
    # Title podle dané struktury
    h1 = soup.select_one("div.content div.book_profile div.book_h h1")
    title = h1.get_text(strip=True) if h1 else None

    # Autoři: .book_about a všechna <a class="book_author">
    author_elems = soup.select("div.book_about a.book_author")
    authors = [a.get_text(" ", strip=True) for a in author_elems if a.get_text(strip=True)]
    authors_str = ", ".join(authors)  # jeden string oddělený čárkou

    return title, authors_str

def fetch_book(book_id: int, timeout: float = 25.0):
    url = build_book_url(book_id)
    r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    r.raise_for_status()

    # Neexistující ID typicky skončí redirectem na homepage → finální URL nebude obsahovat /kniha-<id>
    if f"/kniha-{book_id}" not in r.url:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    title, authors = parse_title_and_authors(soup)
    if not title:
        return None

    return {
        "externalid": book_id,
        "externaltitle": title,
        "externalauthors": authors,
        "externalurl": r.url,  # finální URL po redirectech
    }

class Command(BaseCommand):
    help = (
        "Načte existující CBDB ID z DB (Booksource.sourcetype='CBDB') a v zadaném rozsahu "
        "stáhne pouze chybějící knihy. Výstup zapisuje do JSONL. Do DB nic nezapisuje."
    )

    def add_arguments(self, parser):
        parser.add_argument("--start-id", type=int, required=True, help="Počáteční ID (včetně).")
        parser.add_argument("--end-id", type=int, required=True, help="Koncové ID (včetně).")
        parser.add_argument("--output", required=True, help="Cesta k výstupnímu JSONL (např. div_app/cbdb_books.jsonl).")
        parser.add_argument("--delay", type=float, default=10.0, help="Pauza mezi požadavky v sekundách (default 10).")
        parser.add_argument("--timeout", type=float, default=25.0, help="HTTP timeout v sekundách (default 25).")
        parser.add_argument("--retries", type=int, default=2, help="Počet opakování při chybě (default 2).")
        parser.add_argument("--resume", action="store_true", help="Pokračovat a přidávat na konec existujícího JSONL.")
        parser.add_argument("--skip-jsonl", action="store_true",
                            help="Navíc přeskočit i ID, která už jsou ve výstupním JSONL (kromě DB).")

    def handle(self, *args, **opts):
        start_id: int = opts["start_id"]
        end_id: int = opts["end_id"]
        out_path: str = opts["output"]
        delay: float = float(opts["delay"])
        timeout: float = float(opts["timeout"])
        retries: int = int(opts["retries"])
        resume: bool = bool(opts["resume"])
        skip_jsonl: bool = bool(opts["skip_jsonl"])

        # 1) EXISTUJÍCÍ ID Z DB (pouze čteme)
        existing_ids = set(
            Booksource.objects.filter(sourcetype="CBDB").values_list("externalid", flat=True)
        )
        self.stdout.write(f"V DB nalezeno {len(existing_ids)} CBDB ID (tato přeskočím).")

        # 2) (Volitelně) EXISTUJÍCÍ ID Z JSONL – kvůli resume/duplicitám
        jsonl_ids = set()
        if skip_jsonl and os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8") as rf:
                for line in rf:
                    try:
                        rec = json.loads(line)
                        jsonl_ids.add(int(rec["externalid"]))
                    except Exception:
                        continue
            self.stdout.write(f"V JSONL nalezeno {len(jsonl_ids)} ID (tato také přeskočím).")

        # 3) Otevři výstupní JSONL
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        mode = "a" if (resume and os.path.exists(out_path)) else "w"
        with open(out_path, mode, encoding="utf-8") as jf:
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=retries)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            processed = 0
            downloaded = 0

            step = 1 if end_id >= start_id else -1
            current = start_id

            while True:
                if (step == 1 and current > end_id) or (step == -1 and current < end_id):
                    break

                # přeskoč ID, které už máme v DB nebo (volitelně) už je v JSONL
                if current in existing_ids or (skip_jsonl and current in jsonl_ids):
                    current += step
                    continue

                # požadavek s retriem
                attempt = 0
                data = None
                while True:
                    try:
                        data = fetch_book(current, timeout=timeout)
                        break
                    except requests.RequestException as e:
                        attempt += 1
                        if attempt > retries:
                            self.stderr.write(self.style.WARNING(f"[{current}] Chyba po {retries} pokusech: {e}"))
                            break
                        time.sleep(1.0 * attempt)

                if data:
                    json.dump(data, jf, ensure_ascii=False)
                    jf.write("\n")
                    jf.flush()
                    downloaded += 1
                    # průběžně si zapamatuj, ať v rámci téhož běhu nepíšeme duplicitně
                    jsonl_ids.add(data["externalid"])

                    self.stdout.write(
                        f"[{data['externalid']}] Uloženo: {data['externaltitle']}"
                    )

                # processed += 1
                # if processed % 100 == 0:
                #     self.stdout.write(f"…zpracováno {processed} ID (nově staženo {downloaded})")

                if delay > 0:
                    time.sleep(delay)

                current += step

        self.stdout.write(self.style.SUCCESS(
            f"Hotovo. Prošel jsem {processed} ID, nově staženo {downloaded}. Výstup: {out_path}"
        ))
