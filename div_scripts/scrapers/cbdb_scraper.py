import re
import csv
import time
import sys
from typing import Iterator, Tuple, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

START_URL = "https://www.cbdb.cz/uzivatel-48831-xsilence8x/knihy?booklist_2=1"

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
        book_id = extract_book_id(href)
        if not book_id:
            continue
        title = a.get_text(strip=True) or a.get("title", "").strip()
        if not title:
            continue
        if book_id not in seen:
            seen.add(book_id)
            yield (book_id, title)

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

def iter_all_pages(start_url: str, session: requests.Session) -> Iterator[Tuple[str, str]]:
    url = start_url
    page_idx = 1

    while url:
        resp = session.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for book_id, title in parse_books_from_page(soup):
            yield (book_id, title)

        next_url = find_next_page_url(soup, url)
        if next_url and next_url != url:
            page_idx += 1
            url = next_url
            time.sleep(0.8)
        else:
            break

def main():
    session = requests.Session()

    books = list(iter_all_pages(START_URL, session))

    unique = {}
    for bid, title in books:
        unique.setdefault(bid, title)

    rows = [("book_id", "title")] + [(bid, unique[bid]) for bid in sorted(unique.keys(), key=int)]

    writer = csv.writer(sys.stdout)
    for row in rows:
        writer.writerow(row)

    with open("cbdb_read_books.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    print(f"Uloženo {len(unique)} knih do cbdb_read_books.csv", file=sys.stderr)

if __name__ == "__main__":
    main()
