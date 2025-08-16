# div_management/books/book_duplicate_service.py

"""Správa duplikátov kníh - logika TitleCZ + Author"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from div_content.models import Book, Bookauthor
from ..shared.universal_db_helper import find_existing_book_by_title_author
from ..shared.universal_url_cleaner import normalize_author_name

logger = logging.getLogger('div_management.books.duplicates')

class BookDuplicateService:
    """Service pre správu duplikátov kníh"""
    
    @staticmethod
    def find_duplicate(title: str, author_name: str, external_id: str = None) -> Optional[Book]:
        """
        Nájde duplikát knihy podľa TitleCZ + Author (hlavná logika)
        
        Args:
            title: Názov knihy (titlecz)
            author_name: Meno autora
            external_id: External ID (pre dodatočnú kontrolu)
            
        Returns:
            Book: Existujúca kniha alebo None
        """
        try:
            # 1. Hľadaj podľa external_id ak je zadané
            if external_id:
                book = Book.objects.filter(databazeknih=external_id).first()
                if book:
                    logger.info(f"📚 Nájdená kniha podľa external_id: {external_id}")
                    return book
            
            # 2. Hlavná logika: TitleCZ + Author = unikátna dvojica
            book = find_existing_book_by_title_author(title, author_name)
            if book:
                logger.info(f"📚 Nájdená duplicita: '{title}' + '{author_name}'")
                return book
            
            # 3. Fallback - hľadaj iba podľa názvu (pre knihy bez autora)
            if not author_name:
                book = Book.objects.filter(titlecz=title).first()
                if book:
                    logger.info(f"📚 Nájdená kniha iba podľa názvu: '{title}'")
                    return book
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Chyba pri hľadaní duplikátu '{title}': {e}")
            return None
    
    @staticmethod
    def update_missing_fields(existing_book: Book, new_data: Dict[str, Any], force_update: bool = False) -> Dict[str, Any]:
        """
        Aktualizuje CHYBĚJÍCÍ polia v existujúcej knihe
        
        Args:
            existing_book: Existujúca kniha
            new_data: Nové dáta zo scrapera
            force_update: Vynúti aktualizáciu aj neprázdnych polí
            
        Returns:
            Dict: Report o aktualizácii
        """
        try:
            report = {
                'updated_fields': [],
                'conflicts': [],
                'skipped_fields': [],
                'changed': False
            }
            
            # Mapovanie polí na aktualizáciu
            field_mapping = {
                'year': new_data.get('year'),
                'pages': new_data.get('pages'),
                'language': new_data.get('language'),
                'description': new_data.get('description'),
                'databazeknih': new_data.get('external_id'),
                'img': 'noimg.png',  # Bude aktualizované v image service
            }
            
            # Vždy aktualizované polia
            always_update = ['lastupdated', 'databazeknih']
            
            # Nikdy neaktualizované polia
            never_update = ['bookid', 'url', 'divrating', 'titlecz', 'title']
            
            for field, new_value in field_mapping.items():
                if field in never_update:
                    continue
                
                if not new_value and field not in always_update:
                    continue
                
                current_value = getattr(existing_book, field, None)
                
                # Ak je pole prázdne alebo force_update
                if not current_value or force_update or field in always_update:
                    if current_value and current_value != new_value and field not in always_update:
                        # Loguj konflikt
                        conflict = BookDuplicateService._detect_conflict(field, current_value, new_value)
                        if conflict:
                            report['conflicts'].append(conflict)
                            logger.warning(f"⚠️ Konflikt {field}: '{current_value}' vs '{new_value}'")
                        
                        if not force_update:
                            report['skipped_fields'].append(field)
                            continue
                    
                    # Aktualizuj pole
                    setattr(existing_book, field, new_value)
                    report['updated_fields'].append(field)
                    report['changed'] = True
                    
                    logger.info(f"✅ Aktualizované {field}: '{current_value}' -> '{new_value}'")
                else:
                    report['skipped_fields'].append(field)
            
            # Vždy aktualizuj last_updated
            existing_book.lastupdated = datetime.now().date()
            report['updated_fields'].append('lastupdated')
            report['changed'] = True
            
            # Ulož zmeny
            if report['changed']:
                existing_book.save()
                logger.info(f"💾 Kniha '{existing_book.titlecz}' aktualizovaná")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Chyba pri aktualizácii knihy {existing_book.bookid}: {e}")
            return {'updated_fields': [], 'conflicts': [], 'skipped_fields': [], 'changed': False}
    
    @staticmethod
    def _detect_conflict(field: str, current_value: Any, new_value: Any) -> Optional[Dict[str, Any]]:
        """
        Detekuje významné konflikty medzi hodnotami
        
        Args:
            field: Názov poľa
            current_value: Aktuálna hodnota
            new_value: Nová hodnota
            
        Returns:
            Dict: Informácie o konflikte alebo None
        """
        # Konfigurácia významných rozdielov
        significant_differences = {
            'year': 2,           # Rozdiel 2+ rokov
            'pages': 50,         # Rozdiel 50+ stránok
            'price_percent': 20, # Rozdiel 20%+ v cene
        }
        
        try:
            if field == 'year':
                if abs(int(current_value) - int(new_value)) >= significant_differences['year']:
                    return {
                        'field': field,
                        'current': current_value,
                        'new': new_value,
                        'type': 'significant_year_difference'
                    }
            
            elif field == 'pages':
                if abs(int(current_value) - int(new_value)) >= significant_differences['pages']:
                    return {
                        'field': field,
                        'current': current_value,
                        'new': new_value,
                        'type': 'significant_pages_difference'
                    }
            
            elif field in ['title', 'titlecz', 'author']:
                # Text polia - akýkoľvek rozdiel je významný
                if str(current_value).strip() != str(new_value).strip():
                    return {
                        'field': field,
                        'current': current_value,
                        'new': new_value,
                        'type': 'text_difference'
                    }
            
            return None
            
        except (ValueError, TypeError):
            # Ak nie je možné porovnať, považuj za konflikt
            return {
                'field': field,
                'current': current_value,
                'new': new_value,
                'type': 'comparison_error'
            }

