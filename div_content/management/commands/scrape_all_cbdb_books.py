from __future__ import annotations

import json
import os
import re
import time
from typing import Iterable, Optional, Tuple, List

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
}

BOOK_PATH_RE = re.compile(r"/kniha-(\d+)(?:-|$)", re.IGNORECASE)


def build_book_url(book_id: int) -> str:
    return f"https://cbdb.cz/kniha-{book_id}"


def is_same_book_url(url: str, book_id: int) -> bool:
    """
    Ověří, že výsledná URL opravdu patří k /kniha-<book_id>-... (tj. nebyl redirect na homepage).
    """
    m = BOOK_PATH_RE.search(url)
    return bool(m and int(m.group(1)) == int(book_id))


def parse_title_and_authors(soup: BeautifulSoup) -> Tuple[Optional[str], str]:
    """
    Title:
      <div class="content"><div class="book_profile"><div class="book_h"><h1>...</h1></div>
    Autoři:
      <div class="book_about">
        <a class="book_author" href="autor-...">Autor 1</a>, <a class="book_author" ...>Autor 2</a>, ...
      </div>
    Výstup autorů: jeden řetězec s ", " mezi jmény.
    """
    # přesný h1 podle zadání
    h1 = soup.select_one("div.content div.book_profile div.book_h h1")
    title = (h1.get_text(strip=True) if h1 else None) or None

    # fallback pro jistotu (kdyby šablona občas chyběla)
    if not title:
        og = soup.find("meta", attrs={"property": "og:title"})
        if og and og.get("content"):
            title = og["content"].strip() or None

    # autoři – všechny <a class="book_author"> v rámci .book_about
    author_elems = soup.select("div.book_about a.book_author")
    authors_list = []
    for a in author_elems:
        name = a.get_text(" ", strip=True)
        if name:
            authors_list.append(name)
    # sloučit do jednoho stringu čárkou
    authors_joined = ", ".join(authors_list)

    return title, authors_joined


def fetch_book(session: requests.Session, book_id: int, timeout: float) -> Optional[dict]:
    """
    Vrátí dict s daty knihy, nebo None pokud ID neexistuje (redirect na homepage / chybí title).
    """
    url = build_book_url(book_id)
    r = session.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    r.raise_for_status()

    # neexistující kniha typicky skončí na homepage → výsledná URL neodpovídá /kniha-<id>
    if not is_same_book_url(r.url, book_id):
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    title, authors_joined = parse_title_and_authors(soup)

    if not title:
        return None  # bez titulu považuj za neplatné

    return {
        "externalid": book_id,
        "externaltitle": title,
        "externalauthors": authors_joined,  # jeden string, autoři oddělení čárkou
        "externalurl": r.url,               # finální URL po případných redirectech
    }


def iter_ids(start_id: int, end_id: int) -> Iterable[int]:
    step = 1 if end_id >= start_id else -1
    for i in range(start_id, end_id + step, step):
        yield i


class Command(BaseCommand):
    help = "Projede https://cbdb.cz/kniha-<ID> v zadaném rozsahu a existující knihy ukládá do JSONL (1 řádek = 1 kniha)."

    def add_arguments(self, parser):
        parser.add_argument("--start-id", type=int, required=True, help="Počáteční ID (včetně).")
        parser.add_argument("--end-id", type=int, required=True, help="Koncové ID (včetně).")
        parser.add_argument("--output", required=True, help="Cílová cesta k JSONL souboru (např. div_app/cbdb_books.jsonl).")
        parser.add_argument("--delay", type=float, default=0.4, help="Pauza mezi požadavky v sekundách (default: 0.4).")
        parser.add_argument("--timeout", type=float, default=25.0, help="HTTP timeout na jeden request (default: 25).")
        parser.add_argument("--retries", type=int, default=2, help="Počet opakování při chybě (default: 2).")
        parser.add_argument("--resume", action="store_true", help="Pokračovat do existujícího souboru (append).")

    def handle(self, *args, **opts):
        start_id = opts["start_id"]
        end_id = opts["end_id"]
        out_path = opts["output"]
        delay = float(opts["delay"])
        timeout = float(opts["timeout"])
        retries = int(opts["retries"])
        resume = bool(opts["resume"])

        # výstupní složka
        folder = os.path.dirname(out_path) or "."
        os.makedirs(folder, exist_ok=True)

        mode = "a" if (resume and os.path.exists(out_path)) else "w"
        with open(out_path, mode, encoding="utf-8") as f:
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=retries)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            processed = 0
            found = 0

            if resume and mode == "a":
                self.stderr.write(self.style.WARNING(f"(resume) Zapisuji na konec souboru: {out_path}"))

            for book_id in iter_ids(start_id, end_id):
                # retries s jednoduchým backoffem
                attempt = 0
                while True:
                    try:
                        data = fetch_book(session, book_id, timeout=timeout)
                        break
                    except requests.RequestException as e:
                        attempt += 1
                        if attempt > retries:
                            self.stderr.write(self.style.WARNING(f"[{book_id}] Chyba po {retries} pokusech: {e}"))
                            data = None
                            break
                        time.sleep(1.0 * attempt)

                if data:
                    json.dump(data, f, ensure_ascii=False)
                    f.write("\n")
                    f.flush()
                    found += 1

                processed += 1
                if processed % 100 == 0:
                    self.stdout.write(f"…zpracováno {processed} ID (nalezeno {found})")

                if delay > 0:
                    time.sleep(delay)

        self.stdout.write(self.style.SUCCESS(
            f"Hotovo. Zpracováno {processed} ID, nalezeno {found} knih. Výstup: {out_path}"
        ))
