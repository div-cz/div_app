from __future__ import annotations

import csv
import json
import math
import os
import re
import sys
import time
from typing import Iterator, Optional, Tuple
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError

DEFAULT_URL = "https://www.cbdb.cz/uzivatel-48831-xsilence8x/knihy?booklist_2=1"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
}

BOOK_URL_ID_RE = re.compile(r"/kniha-(\d+)-", re.IGNORECASE)


def extract_book_id(href: str) -> Optional[str]:
    if not href:
        return None
    m = BOOK_URL_ID_RE.search(href)
    return m.group(1) if m else None


def parse_books_from_page(soup: BeautifulSoup) -> Iterator[Tuple[str, str]]:
    seen = set()
    for a in soup.select('a[href*="/kniha-"]'):
        href = a.get("href", "")
        bid = extract_book_id(href)
        if not bid:
            continue
        title = a.get_text(strip=True) or a.get("title", "").strip()
        if not title:
            continue
        if bid not in seen:
            seen.add(bid)
            yield (bid, title)


def find_next_page_url(soup: BeautifulSoup, current_url: str) -> Optional[str]:
    link_next = soup.find("link", rel=lambda v: v and "next" in v.lower())
    if link_next and link_next.get("href"):
        return urljoin(current_url, link_next["href"])

    a_next = soup.find("a", rel=lambda v: v and "next" in v.lower())
    if a_next and a_next.get("href"):
        return urljoin(current_url, a_next["href"])

    for cls in ["next", "pagination__next", "pager__next"]:
        cand = soup.select_one(f"a.{cls}, button.{cls}")
        if cand and cand.get("href"):
            return urljoin(current_url, cand["href"])

    text_candidates = ["další", "›", "»", "next", ">>"]
    for a in soup.select("a"):
        txt = a.get_text(strip=True).lower()
        if txt in text_candidates or any(t in txt for t in text_candidates):
            if a.get("href"):
                return urljoin(current_url, a["href"])
    return None


def _set_query_param(url: str, key: str, value: int | str) -> str:
    """Vrať URL s upraveným/ přidaným query parametrem."""
    u = urlsplit(url)
    q = dict(parse_qsl(u.query, keep_blank_values=True))
    q[str(key)] = str(value)
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(q, doseq=True), u.fragment))

def _parse_total_count(soup: BeautifulSoup) -> int | None:
    """
    Zkus z hlavičky vyčíst 'Přečtené (345)' a vrátit 345.
    """
    m = soup.find(string=re.compile(r"Přečtené\s*\(\s*\d+\s*\)", re.I))
    if not m:
        return None
    m2 = re.search(r"\((\d+)\)", m)
    return int(m2.group(1)) if m2 else None

def _find_max_actual_page(soup: BeautifulSoup) -> int | None:
    """
    Najde nejvyšší číslo stránky z odkazů obsahujících actual_page=.
    """
    pages = []
    for a in soup.select('a[href*="actual_page="]'):
        m = re.search(r'actual_page=(\d+)', a.get('href', ''))
        if m:
            pages.append(int(m.group(1)))
    return max(pages) if pages else None

def iter_all_pages(start_url: str, session: requests.Session, delay: float, max_pages: int | None) -> Iterator[Tuple[str, str]]:
    """
    Stránkování přes parametr ?actual_page=N.
    - 1) stáhne 1. stránku (bez/ s actual_page),
    - 2) spočítá per_page a zkusí odhadnout celkový počet stránek
         (z 'Přečtené (X)' nebo z odkazů s actual_page),
    - 3) iteruje stránky 2..N; pokud N neznáme, jede,
         dokud nepřestanou přibývat nové knihy.
    """
    # první stránka
    resp = session.get(start_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    first_page_books = list(parse_books_from_page(soup))
    seen_ids = set()
    for bid, title in first_page_books:
        seen_ids.add(bid)
        yield (bid, title)

    per_page = len(first_page_books)
    total = _parse_total_count(soup)
    # odhad počtu stránek
    page_count = None
    if total and per_page:
        page_count = math.ceil(total / per_page)
    else:
        page_count = _find_max_actual_page(soup)

    # respektuj --max-pages (pokud je)
    if max_pages:
        page_count = min(page_count or max_pages, max_pages)

    # iteruj od druhé stránky
    page = 2
    while True:
        if page_count and page > page_count:
            break

        url = _set_query_param(start_url, "actual_page", page)
        r = session.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 404:
            break
        r.raise_for_status()
        s = BeautifulSoup(r.text, "html.parser")

        page_books = list(parse_books_from_page(s))
        if not page_books:
            # prázdná stránka = konec
            break

        new_on_page = 0
        for bid, title in page_books:
            if bid not in seen_ids:
                seen_ids.add(bid)
                new_on_page += 1
                yield (bid, title)

        # když neznáme page_count a nepřibylo nic nového → konec
        if not page_count and new_on_page == 0:
            break

        page += 1
        if delay > 0:
            time.sleep(delay)

class Command(BaseCommand):
    help = "Nascrapuje přečtené knihy z CBDB (ID + název) a zapíše je do CSV nebo na stdout."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default=DEFAULT_URL,
            help="Výchozí URL seznamu (default: %(default)s)",
        )
        parser.add_argument(
            "--output",
            default="",
            help="Cesta k výstupnímu CSV (pokud nezadáš, vypíše na stdout).",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.8,
            help="Pauza mezi stránkami v sekundách (default: %(default)s).",
        )
        parser.add_argument(
            "--max-pages",
            type=int,
            default=None,
            help="Maximální počet stránek k projití (pro debug).",
        )
        parser.add_argument(
            "--timeout",
            type=float,
            default=30.0,
            help="HTTP timeout v sekundách na jeden request (default: %(default)s).",
        )

    def handle(self, *args, **options):
        url: str = options["url"]
        output_path: str = options["output"]
        delay: float = options["delay"]
        max_pages: Optional[int] = options["max_pages"]
        timeout: float = options["timeout"]

        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.request = self._wrap_timeout(session.request, timeout)

        try:
            books = list(iter_all_pages(url, session, delay=delay, max_pages=max_pages))
        except requests.HTTPError as e:
            raise CommandError(f"HTTP error: {e.response.status_code} {e.response.reason}")
        except requests.RequestException as e:
            raise CommandError(f"Request error: {e}")
        except Exception as e:
            raise CommandError(str(e))

        # Dedup podle ID
        unique = {}
        for bid, title in books:
            unique.setdefault(bid, title)

        # Seřadit podle číselného ID
        rows = [("book_id", "title")] + [(bid, unique[bid]) for bid in sorted(unique.keys(), key=int)]

        if output_path:
            # základní cesta bez přípony
            base, ext = os.path.splitext(output_path)
            if not ext:  # uživatel zadal jen "books"
                base = output_path

            # zajisti složku
            os.makedirs(os.path.dirname(base) or ".", exist_ok=True)

            # 1) CSV
            csv_path = base + ".csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["book_id", "title"])
                for bid in sorted(unique.keys(), key=int):
                    writer.writerow([bid, unique[bid]])

            # 2) JSON
            json_path = base + ".json"
            data = [{"book_id": int(bid), "title": unique[bid]} for bid in sorted(unique.keys(), key=int)]
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Uloženo {len(unique)} knih do:\n - {csv_path}\n - {json_path}"
                )
            )
        else:
            # fallback: výstup na stdout jako CSV
            writer = csv.writer(sys.stdout)
            writer.writerow(["book_id", "title"])
            for bid in sorted(unique.keys(), key=int):
                writer.writerow([bid, unique[bid]])
            self.stderr.write(self.style.WARNING(f"(Info) Vypsáno {len(unique)} knih na stdout"))

    @staticmethod
    def _wrap_timeout(original_request, timeout: float):
        def wrapped(method, url, **kwargs):
            if "timeout" not in kwargs:
                kwargs["timeout"] = timeout
            return original_request(method, url, **kwargs)
        return wrapped
