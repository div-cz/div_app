# -------------------------------------------------------------------
# div_management/shared/universal_validators.py
# -------------------------------------------------------------------

"""Univerzálne validácie pre všetky moduly"""

import re
from typing import Dict, Any, List

def validate_book_data(data: Dict[str, Any]) -> bool:
    """
    Validuje základné dáta knihy
    
    Args:
        data: Dáta knihy
        
    Returns:
        bool: True ak sú dáta platné
    """
    # Povinný názov
    if not data.get('title', '').strip():
        return False
    
    # Validácia roku
    year = data.get('year')
    if year and (not isinstance(year, int) or year < 1000 or year > 2030):
        return False
    
    # Validácia stránok
    pages = data.get('pages')
    if pages and (not isinstance(pages, int) or pages < 1 or pages > 10000):
        return False
    
    # Validácia ISBN
    isbn = data.get('isbn')
    if isbn and not validate_isbn(isbn):
        return False
    
    return True

def validate_isbn(isbn: str) -> bool:
    """Validuje ISBN formát"""
    if not isbn:
        return True  # ISBN nie je povinný
    
    clean = re.sub(r'[^\dX]', '', str(isbn).upper())
    return len(clean) in [10, 13]

def validate_url_slug(slug: str) -> bool:
    """Validuje URL slug"""
    if not slug:
        return False
    
    # Iba malé písmená, čísla a pomlčky
    return bool(re.match(r'^[a-z0-9-]+$', slug))

def validate_author_name(name: str) -> bool:
    """Validuje meno autora"""
    if not name:
        return True  # Autor nie je povinný
    
    # Minimálne 2 znaky, iba písmená, medzery a pomlčky
    return len(name.strip()) >= 2 and bool(re.match(r'^[a-zA-ZÀ-ÿ\s\-\.]+$', name))

def validate_external_id(external_id: str) -> bool:
    """Validuje external ID"""
    if not external_id:
        return False
    
    # Formát: D-12345 (písmeno-čísla)
    return bool(re.match(r'^[A-Z]-\d+$', external_id))

def sanitize_description(description: str) -> str:
    """Vyčistí popis od nežiaducich znakov"""
    if not description:
        return ""
    
    # Odstráň HTML tagy
    clean = re.sub(r'<[^>]+>', '', description)
    
    # Odstráň prebytočné medzery
    clean = re.sub(r'\s+', ' ', clean)
    
    # Špecifické čistenie pre Dobrovský
    if clean.strip() == "Sdílet":
        return ""
    
    return clean.strip()


