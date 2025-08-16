# ================================================================

# div_management/books/__init__.py

"""
Books modul pre správu kníh

Hlavné triedy:
- BookUpdateService: Hlavný service pre aktualizáciu
- BookDuplicateService: Správa duplikátov  
- BookImageService: Správa obrázkov
- BookURLGenerator: Generovanie URL
"""

from .book_update_service import BookUpdateService
from .book_duplicate_service import BookDuplicateService
from .book_image_service import BookImageService
from .book_utils import BookURLGenerator, BookFieldValidator, BookDataCleaner

__all__ = [
    'BookUpdateService',
    'BookDuplicateService', 
    'BookImageService',
    'BookURLGenerator',
    'BookFieldValidator',
    'BookDataCleaner'
]