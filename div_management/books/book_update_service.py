# ================================================================

# div_management/books/book_update_service.py

"""Hlavný service pre aktualizáciu kníh"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.db import transaction

from div_content.models import Book, Bookwriters, Bookgenre
from ..scraping.dobrovsky_scraper import DobroskyScraper
from ..shared.universal_db_helper import get_or_create_author, get_or_create_genre
from .book_duplicate_service import BookDuplicateService
from .book_image_service import BookImageService
from .book_utils import BookURLGenerator

logger = logging.getLogger('div_management.books.update')

class BookUpdateService:
    """Hlavný service pre aktualizáciu kníh z externých zdrojov"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.scraper = DobroskyScraper()
        self.duplicate_service = BookDuplicateService()
        self.image_service = BookImageService()
        self.url_generator = BookURLGenerator()
        
        # Štatistiky
        self.stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def update_books_from_dobrovsky(self, limit: int = 200, force_update: bool = False) -> Dict[str, int]:
        """
        Hlavná metóda pre aktualizáciu kníh z Dobrovský
        
        Args:
            limit: Počet kníh na spracovanie
            force_update: Vynúti aktualizáciu existujúcich kníh
            
        Returns:
            Dict: Štatistiky spracovania
        """
        start_time = datetime.now()
        logger.info(f"🚀 Začínam aktualizáciu kníh z Dobrovský (limit: {limit})")
        
        try:
            # Získaj zoznam kníh
            books_list = self.scraper.get_books_list(limit=limit)
            
            if not books_list:
                logger.warning("⚠️ Žiadne knihy na spracovanie")
                return self.stats
            
            logger.info(f"📥 Získaných {len(books_list)} kníh na spracovanie")
            
            # Spracuj knihy
            for i, book_data in enumerate(books_list, 1):
                try:
                    logger.debug(f"📖 [{i}/{len(books_list)}] {book_data.get('title', 'N/A')}")
                    self._process_single_book(book_data, force_update)
                    
                except Exception as e:
                    logger.error(f"❌ Chyba pri spracovaní knihy {book_data.get('title', 'N/A')}: {e}")
                    self.stats['errors'] += 1
            
            duration = datetime.now() - start_time
            logger.info(f"✅ Dokončené za {duration.total_seconds():.1f}s")
            logger.info(f"📊 Štatistiky: {self.stats}")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"❌ Kritická chyba pri aktualizácii: {e}")
            raise
    
    def _process_single_book(self, book_data: Dict[str, Any], force_update: bool = False):
        """Spracuje jednu knihu"""
        
        title = book_data.get('title', '').strip()
        author_name = book_data.get('author_name', '').strip()
        external_id = book_data.get('external_id', '')
        
        if not title:
            logger.warning("⚠️ Kniha bez názvu, preskakujem")
            self.stats['skipped'] += 1
            return
        
        if self.dry_run:
            logger.info(f"🔍 DRY RUN - {title} ({author_name})")
            self.stats['skipped'] += 1
            return
        
        try:
            with transaction.atomic():
                # Kontrola duplikátov (TitleCZ + Author logika)
                existing_book = self.duplicate_service.find_duplicate(title, author_name, external_id)
                
                if existing_book:
                    # Aktualizuj existujúcu knihu
                    report = self.duplicate_service.update_missing_fields(
                        existing_book, book_data, force_update
                    )
                    
                    if report['changed']:
                        self.stats['updated'] += 1
                        action = "aktualizovaná"
                        
                        # Spracuj obrázok ak sa zmenil
                        if book_data.get('image_url'):
                            self._process_book_image(existing_book, book_data['image_url'])
                        
                        # Spracuj žáner ak chýba
                        if book_data.get('category'):
                            self._process_book_genre(existing_book, book_data['category'])
                    else:
                        self.stats['skipped'] += 1
                        action = "preskočená (bez zmien)"
                else:
                    # Vytvor novú knihu
                    new_book = self._create_new_book(book_data)
                    self.stats['created'] += 1
                    action = "vytvorená"
                    existing_book = new_book
                
                # Spracuj autora v BookWriters
                if author_name:
                    self._process_book_author(existing_book, author_name)
                
                logger.info(f"✅ '{title}' - {action}")
                self.stats['processed'] += 1
                
        except Exception as e:
            logger.error(f"❌ Chyba pri spracovaní '{title}': {e}")
            self.stats['errors'] += 1
            raise
    
    def _create_new_book(self, book_data: Dict[str, Any]) -> Book:
        """Vytvorí novú knihu"""
        
        # Spracuj autora
        author_id = None
        if book_data.get('author_name'):
            author_id = get_or_create_author(book_data['author_name'])
        
        # Vygeneruj unikátne URL
        unique_url = self.url_generator.generate_unique_book_url(
            book_data['title'],
            book_data.get('author_name', '')
        )
        
        # Vytvor knihu
        book = Book.objects.create(
            title=book_data.get('title', ''),
            titlecz=book_data.get('title_cz', book_data.get('title', '')),
            author=book_data.get('author_name', ''),
            authorid_id=author_id,
            year=book_data.get('year'),
            pages=book_data.get('pages'),
            language=book_data.get('language'),
            description=book_data.get('description', ''),
            databazeknih=book_data.get('external_id'),
            url=unique_url,
            img='noimg.png',
            divrating=0
        )
        
        # Spracuj obrázok
        if book_data.get('image_url'):
            self._process_book_image(book, book_data['image_url'])
        
        # Spracuj žáner
        if book_data.get('category'):
            self._process_book_genre(book, book_data['category'])
        
        return book
    
    def _process_book_image(self, book: Book, image_url: str):
        """Spracuje obrázok knihy"""
        try:
            new_image_path = self.image_service.download_book_image(
                book.bookid,
                book.url,
                image_url
            )
            
            if new_image_path != 'noimg.png' and new_image_path != book.img:
                book.img = new_image_path
                book.save()
                logger.debug(f"🖼️ Obrázok aktualizovaný: {new_image_path}")
                
        except Exception as e:
            logger.warning(f"⚠️ Chyba pri spracovaní obrázka: {e}")
    
    def _process_book_genre(self, book: Book, category: str):
        """Spracuje žáner knihy"""
        try:
            # Extrahuj žáner z kategórie
            genre_name = category.strip().split('/')[-1].strip()
            
            if not genre_name:
                return
            
            # Vytvor žáner ak neexistuje
            genre_id = get_or_create_genre(genre_name)
            
            if genre_id:
                # Priraď žáner ku knihe ak ešte nie je priradený
                Bookgenre.objects.get_or_create(
                    bookid=book,
                    genreid_id=genre_id
                )
                logger.debug(f"🏷️ Žáner priradený: {genre_name}")
                
        except Exception as e:
            logger.warning(f"⚠️ Chyba pri spracovaní žánru: {e}")
    
    def _process_book_author(self, book: Book, author_name: str):
        """Spracuje autora v BookWriters"""
        try:
            author_id = get_or_create_author(author_name)
            
            if author_id:
                # Prepoj autora s knihou ak ešte nie je prepojený
                Bookwriters.objects.get_or_create(
                    book_id=book.bookid,
                    author_id=author_id
                )
                logger.debug(f"👤 Autor prepojený: {author_name}")
                
        except Exception as e:
            logger.warning(f"⚠️ Chyba pri prepojení autora: {e}")

