# -------------------------------------------------------------------
# div_management/scraping/dobrovsky_normalizer.py
# -------------------------------------------------------------------


"""Normalizácia dát z Dobrovský do štandardného formátu"""

import re
import logging
from typing import Dict, Any, List, Optional

from ..configs.dobrovsky_config import (
    DOBROVSKY_FIELD_MAPPING,
    DOBROVSKY_LANGUAGE_MAPPING,
    DOBROVSKY_GENRE_MAPPING,
    DOBROVSKY_SPECIFIC
)
from ..shared.universal_url_cleaner import (
    extract_year_from_text,
    extract_pages_from_text,
    clean_isbn,
    clean_text
)

class DobrovskyNormalizer:
    """Normalizácia dát z Dobrovský"""
    
    @staticmethod
    def normalize_book_data(raw_book: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizuje základné dáta knihy z Dobrovský API/HTML
        
        Args:
            raw_book: Surové dáta z Dobrovský
            
        Returns:
            Dict: Normalizované dáta
        """
        try:
            # Mapovanie základných pol