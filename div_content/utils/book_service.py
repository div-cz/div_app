# div_content/utils/book_service.py
"""
Service pro správu knih a BookSource
Zajišťuje evidenci externích zdrojů a párování s knihami
"""

import logging
from typing import Dict, Optional, Tuple
from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify

from div_content.models import Book, Booksource
from div_content.utils.dobrovsky_scraper import DobrovskyBook

logger = logging.getLogger(__name__)


class BookSourceService:
    """Service pro správu BookSource a párování knih"""

    SOURCE_DOBROVSKY = 'DOBROVSKY'
    SOURCE_CBDB = 'CBDB'
    SOURCE_DB = 'DB'

    def __init__(self):
        self.stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'books_created': 0,
            'books_matched': 0
        }

    def process_dobrovsky_book(self, dob_book: DobrovskyBook, force_update: bool = False) -> Tuple[bool, str]:
        """
        Zpracuje knihu z Dobrovského

        Returns:
            (success, message)
        """
        try:
            self.stats['processed'] += 1

            # Kontrola, zda už záznam v BookSource existuje
            existing_source = Booksource.objects.filter(
                sourcetype=self.SOURCE_DOBROVSKY,
                externalid=dob_book.external_id
            ).first()

            # Vyčisti název (odstraň "Název" suffix)
            clean_title = self._clean_title(dob_book.title)
            clean_author = self._clean_author(dob_book.author)

            if existing_source and not force_update:
                logger.info(f"⏭️ Kniha už existuje v BookSource: {clean_title} (ID: {dob_book.external_id})")
                self.stats['skipped'] += 1
                return True, 'skipped'

            # Pokus o párování s existující knihou
            book = self._find_matching_book(clean_title, clean_author)

            if book:
                logger.info(f"✅ Spárována s existující knihou BookID={book.bookid}: {clean_title}")
                self.stats['books_matched'] += 1
            else:
                # Vytvoř novou knihu
                book = self._create_new_book(clean_title, clean_author, dob_book)
                logger.info(f"📚 Vytvořena nová kniha BookID={book.bookid}: {clean_title}")
                self.stats['books_created'] += 1

            # Ulož/aktualizuj BookSource
            if existing_source:
                # Aktualizuj existující
                existing_source.bookid = book
                existing_source.externaltitle = dob_book.title
                existing_source.externalauthors = dob_book.author
                existing_source.externalurl = dob_book.url
                existing_source.save()

                logger.info(f"🔄 Aktualizován BookSource ID={existing_source.booksourceid}")
                self.stats['updated'] += 1
            else:
                # Vytvoř nový
                Booksource.objects.create(
                    bookid=book,
                    sourcetype=self.SOURCE_DOBROVSKY,
                    externalid=dob_book.external_id,
                    externaltitle=dob_book.title,
                    externalauthors=dob_book.author,
                    externalurl=dob_book.url
                )

                logger.info(f"✨ Vytvořen nový BookSource pro ExternalID={dob_book.external_id}")
                self.stats['created'] += 1

            return True, 'success'

        except Exception as e:
            logger.error(f"❌ Chyba při zpracování knihy {dob_book.title}: {e}", exc_info=True)
            self.stats['errors'] += 1
            return False, f'error: {str(e)}'

    def _clean_title(self, title: str) -> str:
        """
        Vyčistí název knihy od klíčových slov jako "Název"

        Např: "Pod letní oblohou Název" -> "Pod letní oblohou"
        """
        if not title:
            return ""

        # Odstraň suffix " Název" (case insensitive)
        import re
        clean = re.sub(r'\s+Název\s*$', '', title, flags=re.IGNORECASE)
        clean = re.sub(r'\s+Name\s*$', '', clean, flags=re.IGNORECASE)

        return clean.strip()

    def _clean_author(self, author: str) -> str:
        """Vyčistí jméno autora"""
        if not author:
            return ""
        return author.strip()

    def _find_matching_book(self, title: str, author: str) -> Optional[Book]:
        """
        Najde existující knihu podle názvu a autora

        Párování: název + autor (unikátní kombinace)
        """
        if not title or not author:
            return None

        # Hledáme podle titlu (TitleCZ nebo Title) a autora
        books = Book.objects.filter(
            Q(titlecz__iexact=title) | Q(title__iexact=title),
            author__iexact=author
        )

        if books.count() == 1:
            return books.first()
        elif books.count() > 1:
            # Pokud najdeme více knih, vybereme první
            logger.warning(f"⚠️ Nalezeno více knih pro '{title}' + '{author}': {books.count()}")
            return books.first()

        return None

    def _create_new_book(self, title: str, author: str, dob_book: DobrovskyBook) -> Book:
        """
        Vytvoří novou knihu v databázi

        Args:
            title: Vyčištěný název
            author: Vyčištěný autor
            dob_book: Původní data z Dobrovského

        Returns:
            Nová instance Book
        """
        # Generuj jedinečné URL
        url = self._generate_unique_url(title, author)

        # Vytvoř knihu
        book = Book.objects.create(
            title=title,
            titlecz=title,
            author=author,
            url=url,
            sourcetype=self.SOURCE_DOBROVSKY,
            sourceid=dob_book.external_id,
            divrating=50,  # Nastavíme rating 50 pro novinky
            language='cs',
            img='noimg.png'  # Default obrázek
        )

        return book

    def _generate_unique_url(self, title: str, author: str) -> str:
        """
        Generuje jedinečné URL pro knihu

        Formát:
        - nazev-knihy (pro první výskyt)
        - nazev-knihy-autor (pro duplicity)
        - nazev-knihy-autor-2 (pro další duplicity)
        """
        base_slug = slugify(title)

        # Zkusíme nejdřív jen název
        if not Book.objects.filter(url=base_slug).exists():
            return base_slug

        # Pokud existuje, přidáme autora
        slug_with_author = f"{base_slug}-{slugify(author)}"

        if not Book.objects.filter(url=slug_with_author).exists():
            return slug_with_author

        # Pokud i to existuje, přidáme číslo
        counter = 2
        while True:
            slug = f"{slug_with_author}-{counter}"
            if not Book.objects.filter(url=slug).exists():
                return slug
            counter += 1

    def get_stats(self) -> Dict:
        """Vrátí statistiky zpracování"""
        return self.stats.copy()

    def reset_stats(self):
        """Resetuje statistiky"""
        for key in self.stats:
            self.stats[key] = 0


def process_dobrovsky_books(books: list, force_update: bool = False) -> Dict:
    """
    Helper funkce pro zpracování seznamu knih z Dobrovského

    Args:
        books: Seznam DobrovskyBook objektů
        force_update: Zda aktualizovat i existující záznamy

    Returns:
        Slovník se statistikami
    """
    service = BookSourceService()

    logger.info(f"📥 Začínám zpracování {len(books)} knih")

    for book in books:
        service.process_dobrovsky_book(book, force_update=force_update)

    stats = service.get_stats()
    logger.info(f"✅ Zpracování dokončeno: {stats}")

    return stats
