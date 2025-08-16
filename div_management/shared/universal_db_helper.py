# -------------------------------------------------------------------
# div_management/shared/universal_db_helper.py
# -------------------------------------------------------------------


"""Univerzálne DB pomocné funkcie"""

import logging
from typing import Optional
from django.db import transaction

from div_content.models import Bookauthor, Metagenre
from .universal_url_cleaner import clean_url, normalize_author_name

logger = logging.getLogger('div_management.db')

def get_or_create_author(author_name: str) -> Optional[int]:
    """
    Nájde alebo vytvorí autora
    
    Args:
        author_name: Celé meno autora
        
    Returns:
        int: ID autora alebo None
    """
    if not author_name or not author_name.strip():
        return None
    
    try:
        # Rozdelenie mena
        firstname, middlename, lastname = normalize_author_name(author_name)
        
        # Hľadaj existujúceho
        author = Bookauthor.objects.filter(
            firstname=firstname,
            middlename=middlename,
            lastname=lastname
        ).first()
        
        if author:
            return author.authorid
        
        # Vytvor nového
        with transaction.atomic():
            url = generate_unique_author_url(author_name)
            
            author = Bookauthor.objects.create(
                firstname=firstname,
                middlename=middlename,
                lastname=lastname,
                url=url,
                divrating=0
            )
            
            logger.info(f"✅ Vytvorený nový autor: {author_name}")
            return author.authorid
            
    except Exception as e:
        logger.error(f"❌ Chyba pri vytváraní autora '{author_name}': {e}")
        return None

def get_or_create_genre(genre_name: str) -> Optional[int]:
    """
    Nájde alebo vytvorí žáner
    
    Args:
        genre_name: Názov žánru
        
    Returns:
        int: ID žánru alebo None
    """
    if not genre_name or not genre_name.strip():
        return None
    
    try:
        genre_name = genre_name.strip()
        
        # Hľadaj podľa českého názvu
        genre = Metagenre.objects.filter(genrenamecz=genre_name).first()
        
        if genre:
            return genre.genreid
        
        # Vytvor nový
        with transaction.atomic():
            url = clean_url(genre_name)
            
            genre = Metagenre.objects.create(
                genrename=genre_name,
                genrenamecz=genre_name,
                url=url
            )
            
            logger.info(f"✅ Vytvorený nový žáner: {genre_name}")
            return genre.genreid
            
    except Exception as e:
        logger.error(f"❌ Chyba pri vytváraní žánru '{genre_name}': {e}")
        return None

def generate_unique_author_url(author_name: str) -> str:
    """Vygeneruje unikátne URL pre autora"""
    base_url = clean_url(author_name)
    url = base_url
    counter = 2
    
    while Bookauthor.objects.filter(url=url).exists():
        url = f"{base_url}-{counter}"
        counter += 1
    
    return url

def find_existing_book_by_title_author(title: str, author_name: str):
    """
    Nájde existujúcu knihu podľa názvu a autora (logika duplikátov)
    
    Args:
        title: Názov knihy (titlecz)
        author_name: Meno autora
        
    Returns:
        Book: Existujúca kniha alebo None
    """
    from div_content.models import Book
    
    if not title:
        return None
    
    # Hľadaj podľa názvu + autora (logika duplikátov)
    if author_name:
        author = Bookauthor.objects.filter(
            **dict(zip(['firstname', 'middlename', 'lastname'], 
                      normalize_author_name(author_name)))
        ).first()
        
        if author:
            book = Book.objects.filter(
                titlecz=title,
                authorid=author
            ).first()
            if book:
                return book
    
    # Fallback - hľadaj iba podľa názvu
    return Book.objects.filter(titlecz=title).first()