# ================================================================

# div_management/__init__.py

"""
DIV Management System

Systém pre správu obsahu (knihy, filmy, hry) s podporou
web scrapingu a automatickej aktualizácie z externých zdrojov.

Moduly:
- books: Správa kníh (Dobrovský, Databáze knih, ...)
- movies: Správa filmov (ČSFD, IMDB, ...) - budúce
- games: Správa hier (Steam, Epic, ...) - budúce
- scraping: Web scraping pre všetky moduly
- shared: Spoločné nástroje a utilities
- configs: Konfigurácie

Použitie:
    python manage.py update_books --limit 100
    python manage.py update_books --dry-run --verbose
"""

__version__ = '1.0.0'
__author__ = 'DIV.cz Team'

# Hlavné triedy pre rýchly import
from .books import BookUpdateService
from .shared.universal_logger import setup_logging

__all__ = [
    'BookUpdateService',
    'setup_logging'
]

