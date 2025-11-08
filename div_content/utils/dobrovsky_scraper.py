# div_content/utils/dobrovsky_scraper.py
"""
Scraper pro Knihy Dobrovský
Stahuje informace o knihách z knihydobrovsky.cz
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class DobrovskyBook:
    """Reprezentace knihy z Dobrovského"""

    def __init__(self,
                 external_id: str,
                 title: str,
                 author: str,
                 url: str,
                 price: Optional[float] = None,
                 image_url: Optional[str] = None):
        self.external_id = external_id
        self.title = title
        self.author = author
        self.url = url
        self.price = price
        self.image_url = image_url

    def __repr__(self):
        return f"DobrovskyBook(id={self.external_id}, title='{self.title}', author='{self.author}')"


class DobrovskyScr:
    """Scraper pro Knihy Dobrovský"""

    BASE_URL = "https://www.knihydobrovsky.cz"
    BOOKS_URL = f"{BASE_URL}/knihy"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        # Komplexnější hlavičky pro obejití základní ochrany
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Cache-Control': 'max-age=0',
        })

    def scrape_books(self, limit: int = 200, sort: int = 1) -> List[DobrovskyBook]:
        """
        Stáhne seznam knih z Dobrovského

        Args:
            limit: Maximální počet knih
            sort: Způsob řazení (1 = nejnovější, 2 = nejprodávanější, atd.)

        Returns:
            Seznam DobrovskyBook objektů
        """
        books = []
        page = 1

        logger.info(f"🚀 Zahajuji scraping Dobrovského (limit: {limit})")

        while len(books) < limit:
            try:
                # Stáhni stránku
                # První stránka nemá currentPage parametr, další mají currentPage=2, 3, ...
                if page == 1:
                    url = f"{self.BOOKS_URL}?sort={sort}"
                else:
                    url = f"{self.BOOKS_URL}?sort={sort}&currentPage={page}"
                logger.info(f"📄 Stahuji stránku {page}: {url}")

                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Parsuj HTML
                soup = BeautifulSoup(response.content, 'html.parser')

                # Najdi produkty
                product_blocks = soup.find_all('div', class_='product-box')

                if not product_blocks:
                    logger.warning(f"⚠️ Žádné produkty na stránce {page}")
                    break

                logger.info(f"📚 Nalezeno {len(product_blocks)} knih na stránce {page}")

                for block in product_blocks:
                    if len(books) >= limit:
                        break

                    try:
                        book = self._parse_book_block(block)
                        if book:
                            books.append(book)
                    except Exception as e:
                        logger.error(f"❌ Chyba při parsování knihy: {e}")
                        continue

                # Pokud jsme na poslední stránce
                if len(product_blocks) < 24:  # Předpokládáme 24 knih na stránku
                    break

                page += 1
                time.sleep(0.5)  # Buď slušný k serveru

            except requests.RequestException as e:
                logger.error(f"❌ Chyba při stahování stránky {page}: {e}")
                break

        logger.info(f"✅ Scraping dokončen: {len(books)} knih")
        return books

    def _parse_book_block(self, block) -> Optional[DobrovskyBook]:
        """Parsuje jeden blok produktu"""

        try:
            # URL a External ID
            link = block.find('a', class_='product-box__link')
            if not link or not link.get('href'):
                return None

            url = link['href']
            if not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"

            # External ID z URL (poslední číslo)
            external_id = self._extract_id_from_url(url)
            if not external_id:
                return None

            # Název knihy
            title_elem = block.find('h3', class_='product-box__title')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Autor
            author_elem = block.find('p', class_='product-box__author')
            author = author_elem.get_text(strip=True) if author_elem else "Neznámý autor"

            # Cena
            price = None
            price_elem = block.find('span', class_='product-box__price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = self._parse_price(price_text)

            # Obrázek
            image_url = None
            img_elem = block.find('img')
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"{self.BASE_URL}{image_url}"

            return DobrovskyBook(
                external_id=external_id,
                title=title,
                author=author,
                url=url,
                price=price,
                image_url=image_url
            )

        except Exception as e:
            logger.error(f"❌ Chyba při parsování bloku: {e}")
            return None

    def _extract_id_from_url(self, url: str) -> Optional[str]:
        """Extrahuje ID z URL (poslední číslo)"""
        # Očekáváme URL jako: https://www.knihydobrovsky.cz/kniha/nazev-647575993
        match = re.search(r'-(\d+)$', url.rstrip('/'))
        return match.group(1) if match else None

    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parsuje cenu z textu"""
        try:
            # Odstraň "Kč" a další znaky, ponechej jen čísla a čárku/tečku
            price_clean = re.sub(r'[^\d,.]', '', price_text)
            price_clean = price_clean.replace(',', '.')
            return float(price_clean) if price_clean else None
        except (ValueError, AttributeError):
            return None


def scrape_dobrovsky_books(limit: int = 200) -> List[DobrovskyBook]:
    """
    Helper funkce pro snadné použití scraperu

    Args:
        limit: Maximální počet knih

    Returns:
        Seznam DobrovskyBook objektů
    """
    scraper = DobrovskyScr()
    return scraper.scrape_books(limit=limit)
