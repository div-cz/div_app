import re
import logging
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper
from ..configs.dobrovsky_config import DOBROVSKY_BASE_CONFIG

class DobroskyScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_config = DOBROVSKY_BASE_CONFIG
        self.logger = logging.getLogger('div_management.scraping.dobrovsky')
    
    def get_books_list(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        try:
            self.logger.info(f"📥 DEBUG: Scraping Dobrovský (limit: {limit})")
            
            url = f"{self.base_config['BASE_URL']}/knihy"
            self.logger.info(f"🌐 DEBUG: URL = {url}")
            
            response = self.make_request('GET', url)
            if not response:
                self.logger.error("❌ DEBUG: Žiadna odpoveď z servera")
                return []
            
            self.logger.info(f"✅ DEBUG: Odpoveď získaná, status: {response.status_code}")
            self.logger.info(f"📄 DEBUG: HTML dĺžka: {len(response.text)} znakov")
            
            # Ukáž prvých 500 znakov HTML pre debug
            html_preview = response.text[:500].replace('\n', ' ')
            self.logger.info(f"🔍 DEBUG: HTML začiatok: {html_preview}")
            
            books = self._debug_parse_html(response.text, limit)
            
            self.logger.info(f"📊 DEBUG: Extrahovaných {len(books)} kníh")
            for i, book in enumerate(books, 1):
                self.logger.info(f"  📖 DEBUG #{i}: '{book['title']}' - '{book['author_name']}'")
            
            return books
            
        except Exception as e:
            self.logger.error(f"❌ DEBUG: Kritická chyba: {e}")
            import traceback
            self.logger.error(f"🔥 DEBUG: Traceback: {traceback.format_exc()}")
            return []
    
    def get_book_details(self, book_id: str, book_url: str = None):
        return {}
    
    def _debug_parse_html(self, html: str, limit: int) -> List[Dict[str, Any]]:
        books = []
        
        try:
            # DEBUG: Skús rôzne selektory a ukáž výsledky
            selectors = {
                'product_divs': r'<div[^>]*class="[^"]*product[^"]*"[^>]*>',
                'item_divs': r'<div[^>]*class="[^"]*item[^"]*"[^>]*>',
                'book_divs': r'<div[^>]*class="[^"]*book[^"]*"[^>]*>',
                'articles': r'<article[^>]*>',
                'h_tags': r'<h[1-6][^>]*>',
                'links_with_kniha': r'<a[^>]*href="[^"]*kniha[^"]*"',
                'all_links': r'<a[^>]*href=',
            }
            
            for name, pattern in selectors.items():
                matches = re.findall(pattern, html, re.IGNORECASE)
                self.logger.info(f"🔍 DEBUG: {name} = {len(matches)} zhodí")
            
            # Skús najjednoduchší prístup - hľadaj všetky H tagy
            h_tags = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', html, re.DOTALL | re.IGNORECASE)
            self.logger.info(f"📝 DEBUG: Našiel {len(h_tags)} H tagov")
            
            # Ukáž prvých 5 H tagov
            for i, h_tag in enumerate(h_tags[:5], 1):
                clean_h = re.sub(r'<[^>]+>', '', h_tag).strip()[:100]
                self.logger.info(f"  🏷️ DEBUG H{i}: {clean_h}")
            
            # Skús nájsť linky
            links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
            self.logger.info(f"🔗 DEBUG: Našiel {len(links)} linkov")
            
            # Ukáž prvých 5 linkov
            for i, (href, text) in enumerate(links[:5], 1):
                clean_text = re.sub(r'<[^>]+>', '', text).strip()[:50]
                self.logger.info(f"  🔗 DEBUG Link{i}: {href} -> {clean_text}")
            
            # Vytvor testovné knihy z H tagov alebo linkov
            sources = h_tags[:limit] if h_tags else [text for href, text in links[:limit]]
            
            for i, source in enumerate(sources):
                clean_title = re.sub(r'<[^>]+>', '', source).strip()
                
                if len(clean_title) > 5:  # Iba ak má rozumný názov
                    book = {
                        'external_id': f'D-debug-{i+1}',
                        'title': clean_title[:100],  # Obmedzenie dĺžky
                        'title_cz': clean_title[:100],
                        'author_name': f'Debug Autor {i+1}',
                        'category': 'Debug Kategória',
                        'year': 2024,
                        'pages': None,
                        'isbn': None,
                        'image_url': '',
                        'product_url': '',
                        'description': 'Debug kniha extrahovaná zo stránky',
                        'publisher': '',
                        'language': 'cs',
                        'price': None,
                    }
                    books.append(book)
            
            return books
            
        except Exception as e:
            self.logger.error(f"❌ DEBUG: Parsing zlyhal: {e}")
            return []
