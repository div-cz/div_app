# -------------------------------------------------------------------
# div_management/scraping/base_scraper.py
# -------------------------------------------------------------------

"""Abstraktná trieda pre všetky scrapery"""

import requests
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from ..configs.scraping_config import UNIVERSAL_SCRAPING_CONFIG

class BaseScraper(ABC):
    """Abstraktná základná trieda pre všetky scrapery"""
    
    def __init__(self):
        self.config = UNIVERSAL_SCRAPING_CONFIG
        self.session = requests.Session()
        self.session.headers.update(self.config['HEADERS'])
        self.logger = logging.getLogger(f'div_management.scraping.{self.__class__.__name__.lower()}')
    
    @abstractmethod
    def get_books_list(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Získa zoznam kníh - musí implementovať každý scraper"""
        pass
    
    @abstractmethod
    def get_book_details(self, book_id: str, book_url: str = None) -> Optional[Dict[str, Any]]:
        """Získa detailné informácie o knihe - musí implementovať každý scraper"""
        pass
    
    def make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Vykoná HTTP request s retry logikou
        
        Args:
            method: HTTP metóda
            url: URL
            **kwargs: Dodatočné parametre pre request
            
        Returns:
            Response alebo None pri chybe
        """
        max_retries = self.config['MAX_RETRIES']
        
        for attempt in range(max_retries):
            try:
                # Rate limiting
                time.sleep(self.config['REQUEST_DELAY'])
                
                response = self.session.request(
                    method, 
                    url, 
                    timeout=self.config['TIMEOUT'],
                    **kwargs
                )
                response.raise_for_status()
                
                return response
                
            except requests.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    self.logger.error(f"All retry attempts failed for {url}")
                    return None
                
                # Exponential backoff
                if self.config['ERROR_HANDLING']['EXPONENTIAL_BACKOFF']:
                    wait_time = min(2 ** attempt, self.config['ERROR_HANDLING']['MAX_BACKOFF_TIME'])
                    time.sleep(wait_time)
        
        return None
    
    def is_valid_response(self, response: requests.Response) -> bool:
        """Kontroluje, či je response platný"""
        if not response:
            return False
        
        content_type = response.headers.get('Content-Type', '')
        
        # Kontrola, či nie je HTML error stránka
        if 'html' in content_type and 'error' in response.text.lower():
            return False
        
        return True

# ===