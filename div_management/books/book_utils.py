# div_management/books/book_utils.py - OPRAVENÁ VERZIA

"""Pomocné utility pre knihy"""

import re
import logging
from typing import Optional

from div_content.models import Book
from ..shared.universal_url_cleaner import clean_url

logger = logging.getLogger('div_management.books.utils')

class BookURLGenerator:
    """Generovanie unikátnych URL pre knihy"""
    
    @staticmethod
    def generate_unique_book_url(title: str, author_name: str = "") -> str:
        """
        Vygeneruje unikátne URL pre knihu
        
        Args:
            title: Názov knihy
            author_name: Meno autora
            
        Returns:
            str: Unikátne URL
        """
        try:
            # Základné URL z názvu
            base_url = clean_url(title)
            
            if not base_url:
                base_url = "kniha"
            
            candidate_url = base_url
            
            # 1. Skús čistý názov
            if not Book.objects.filter(url=candidate_url).exists():
                return candidate_url
            
            # 2. Skús názov + autor
            if author_name:
                author_clean = clean_url(author_name)
                candidate_url = f"{base_url}-{author_clean}"
                if not Book.objects.filter(url=candidate_url).exists():
                    return candidate_url
            
            # 3. Pridávaj čísla
            counter = 2
            while True:
                new_url = f"{candidate_url}-{counter}"
                if not Book.objects.filter(url=new_url).exists():
                    return new_url
                counter += 1
                
                # Bezpečnostný limit
                if counter > 1000:
                    logger.warning(f"⚠️ Dosiahnutý limit pri generovaní URL pre '{title}'")
                    return f"{candidate_url}-{counter}"
                    
        except Exception as e:
            logger.error(f"❌ Chyba pri generovaní URL pre '{title}': {e}")
            return f"kniha-{hash(title) % 10000}"

class BookFieldValidator:
    """Validácie polí špecifické pre knihy"""
    
    @staticmethod
    def validate_title(title: str) -> bool:
        """Validuje názov knihy"""
        if not title or not title.strip():
            return False
        
        if len(title.strip()) < 1 or len(title.strip()) > 255:
            return False
        
        return True
    
    @staticmethod
    def validate_author_name(author_name: str) -> bool:
        """Validuje meno autora"""
        if not author_name:
            return True  # Autor nie je povinný
        
        if len(author_name.strip()) < 2 or len(author_name.strip()) > 255:
            return False
        
        # Iba písmená, medzery, pomlčky a bodky - OPRAVENÝ REGEX
        return bool(re.match(r'^[a-zA-ZÀ-ÿ\s\-\.]+$', author_name.strip()))
    
    @staticmethod
    def validate_year(year: int) -> bool:
        """Validuje rok publikácie"""
        if not year:
            return True  # Rok nie je povinný
        
        return isinstance(year, int) and 1000 <= year <= 2030
    
    @staticmethod
    def validate_pages(pages: int) -> bool:
        """Validuje počet stránok"""
        if not pages:
            return True  # Stránky nie sú povinné
        
        return isinstance(pages, int) and 1 <= pages <= 10000
    
    @staticmethod
    def validate_isbn(isbn: str) -> bool:
        """Validuje ISBN"""
        if not isbn:
            return True  # ISBN nie je povinný
        
        # Odstráň všetko okrem číslic a X
        clean_isbn = re.sub(r'[^\dX]', '', str(isbn).upper())
        return len(clean_isbn) in [10, 13]

class BookDataCleaner:
    """Čistenie dát špecifické pre knihy"""
    
    @staticmethod
    def clean_title(title: str) -> str:
        """Vyčistí názov knihy"""
        if not title:
            return ""
        
        # Odstráň HTML tagy
        clean = re.sub(r'<[^>]+>', '', title)
        
        # Odstráň prebytočné medzery
        clean = re.sub(r'\s+', ' ', clean)
        
        # Trim a skráti ak je príliš dlhý
        clean = clean.strip()
        if len(clean) > 255:
            clean = clean[:252] + "..."
        
        return clean
    
    @staticmethod
    def clean_description(description: str) -> str:
        """Vyčistí popis knihy"""
        if not description:
            return ""
        
        # Odstráň HTML tagy
        clean = re.sub(r'<[^>]+>', '', description)
        
        # Odstráň prebytočné medzery
        clean = re.sub(r'\s+', ' ', clean)
        
        # Špecifické čistenie
        if clean.strip() in ["Sdílet", "Více informací", "Zobrazit více"]:
            return ""
        
        # Skráti ak je príliš dlhý
        if len(clean) > 5000:
            clean = clean[:4997] + "..."
        
        return clean.strip()
    
    @staticmethod
    def extract_genre_from_category(category: str) -> str:
        """Extrahuje žáner z kategórie"""
        if not category:
            return ""
        
        # Vezmi posledný segment (napr. "Knihy/Beletria/Fantasy" -> "Fantasy")
        parts = category.strip().split('/')
        genre = parts[-1].strip()
        
        # Normalizácia známych žánrov
        genre_mapping = {
            'sci-fi': 'Science Fiction',
            'fantasy': 'Fantasy',
            'detektivka': 'Detektívny román',
            'romantika': 'Romantika',
            'thriller': 'Thriller',
            'young adult': 'Literatúra pre mladých',
        }
        
        return genre_mapping.get(genre.lower(), genre)