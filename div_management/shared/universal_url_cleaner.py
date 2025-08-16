# -------------------------------------------------------------------
# div_management/shared/universal_url_cleaner.py
# -------------------------------------------------------------------


"""Univerzálne čistenie URL a textu - použije sa vo všetkých moduloch"""

import re
import unicodedata

def clean_url(text: str) -> str:
    """
    Vyčistí text pre URL slug
    
    Args:
        text: Vstupný text
        
    Returns:
        str: Čistý URL slug
    """
    if not text:
        return ""
    
    # Odstráň diakritiku
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Malé písmená
    text = text.lower()
    
    # Nahraď špeciálne znaky
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Nahraď medzery a viacnásobné pomlčky
    text = re.sub(r'[-\s]+', '-', text)
    
    # Odstráň pomlčky na začiatku/konci
    text = text.strip('-')
    
    # Skráti ak je príliš dlhý
    if len(text) > 100:
        text = text[:100].rstrip('-')
    
    return text

def clean_text(text: str) -> str:
    """Vyčistí text od HTML tagov a prebytočných medzier"""
    if not text:
        return ""
    
    # Odstráň HTML tagy
    text = re.sub(r'<[^>]+>', '', text)
    
    # Odstráň prebytočné medzery
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def normalize_author_name(name: str) -> tuple:
    """
    Rozdelí meno autora na krstné, stredné a priezvisko
    
    Args:
        name: Celé meno autora
        
    Returns:
        tuple: (firstname, middlename, lastname)
    """
    if not name:
        return "", "", ""
    
    parts = clean_text(name).split()
    
    if not parts:
        return "", "", ""
    elif len(parts) == 1:
        return "", "", parts[0]  # Iba priezvisko
    elif len(parts) == 2:
        return parts[0], "", parts[1]  # Meno + priezvisko
    else:
        # Viac častí: prvé je meno, posledné priezvisko, zvyšok stredné
        return parts[0], " ".join(parts[1:-1]), parts[-1]

def extract_year_from_text(text: str) -> int:
    """Extrahuje rok z textu"""
    if not text:
        return None
    
    match = re.search(r'\b(19|20)\d{2}\b', str(text))
    if match:
        year = int(match.group())
        if 1000 <= year <= 2030:
            return year
    return None

def extract_pages_from_text(text: str) -> int:
    """Extrahuje počet stránok z textu"""
    if not text:
        return None
    
    match = re.search(r'\b(\d+)\b', str(text))
    if match:
        pages = int(match.group())
        if 1 <= pages <= 10000:
            return pages
    return None

def clean_isbn(isbn: str) -> str:
    """Vyčistí ISBN"""
    if not isbn:
        return None
    
    clean = re.sub(r'[^\dX]', '', str(isbn).upper())
    return clean if len(clean) in [10, 13] else None


