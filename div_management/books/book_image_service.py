# ================================================================

# div_management/books/book_image_service.py

"""Service pre správu obrázkov kníh"""

import os
import re
import requests
import time
from pathlib import Path
from typing import Optional
import logging

from ..configs.books_config import BOOKS_IMAGE_CONFIG

logger = logging.getLogger('div_management.books.images')

class BookImageService:
    """Service pre sťahovanie a správu obrázkov kníh"""
    
    def __init__(self):
        self.config = BOOKS_IMAGE_CONFIG
        self.base_path = Path(self.config['BASE_PATH'])
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def download_book_image(self, book_id: int, book_url: str, image_url: str) -> str:
        """
        Stiahne obrázok knihy
        
        Args:
            book_id: ID knihy
            book_url: URL slug knihy
            image_url: URL obrázka z Dobrovský
            
        Returns:
            str: Relatívna cesta k obrázku alebo 'noimg.png'
        """
        if not image_url or image_url == "noimg.png":
            return "noimg.png"
        
        try:
            # Extrahuj relatívnu cestu z Dobrovský URL
            relative_path = self._extract_relative_path(image_url)
            if not relative_path:
                logger.warning(f"⚠️ Neplatný image_url: {image_url}")
                return "noimg.png"
            
            # Zostav plnú URL
            full_image_url = f"https://www.knihydobrovsky.cz/thumbs/book-detail-fancy-box/mod_eshop/produkty{relative_path}"
            
            # Nájdi správnu zložku
            folder_num, folder_path = self._get_current_folder()
            
            # Názov súboru
            filename = self.config['FILENAME_PATTERN'].format(
                book_id=book_id,
                book_url=book_url
            )
            save_path = folder_path / filename
            
            # Ak už existuje, vráť cestu
            if save_path.exists():
                relative_result = save_path.relative_to(self.base_path).as_posix()
                logger.info(f"🖼️ Obrázok už existuje: {relative_result}")
                return relative_result
            
            # Stiahni obrázok
            success = self._download_image(full_image_url, save_path)
            
            if success:
                relative_result = save_path.relative_to(self.base_path).as_posix()
                logger.info(f"✅ Obrázok stiahnutý: {relative_result}")
                return relative_result
            else:
                return "noimg.png"
                
        except Exception as e:
            logger.error(f"❌ Chyba pri sťahovaní obrázka pre knihu {book_id}: {e}")
            return "noimg.png"
    
    def _extract_relative_path(self, image_url: str) -> Optional[str]:
        """Extrahuje relatívnu cestu z Dobrovský URL"""
        # Hľadaj /produkty v URL
        match = re.search(r"/produkty(.+)", image_url)
        return match.group(1) if match else None
    
    def _get_current_folder(self) -> tuple[int, Path]:
        """Nájde aktuálnu zložku pre obrázky"""
        start_num = self.config['FOLDER_START_NUMBER']
        max_num = self.config['MAX_FOLDER_NUMBER']
        max_images = self.config['MAX_IMAGES_PER_FOLDER']
        
        # Nájdi najvyššie číslo zložky
        existing_folders = [
            int(f.name) for f in self.base_path.iterdir()
            if f.is_dir() and f.name.isdigit() and start_num <= int(f.name) <= max_num
        ]
        
        folder_num = max(existing_folders, default=start_num)
        folder_path = self.base_path / str(folder_num)
        folder_path.mkdir(exist_ok=True)
        
        # Spočítaj súbory v zložke
        files_count = len(list(folder_path.glob("*")))
        
        # Ak je zložka plná, vytvor novú
        if files_count >= max_images:
            folder_num += 1
            if folder_num > max_num:
                logger.warning(f"⚠️ Dosiahnutý maximálny počet zložiek: {max_num}")
                folder_num = max_num  # Použije poslednú zložku
            
            folder_path = self.base_path / str(folder_num)
            folder_path.mkdir(exist_ok=True)
        
        return folder_num, folder_path
    
    def _download_image(self, image_url: str, save_path: Path) -> bool:
        """Stiahne obrázok z URL"""
        try:
            # Rate limiting
            time.sleep(0.2)
            
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Kontrola content type
            content_type = response.headers.get("Content-Type", "")
            if "html" in content_type.lower():
                logger.warning(f"⚠️ URL nie je obrázok: {image_url}")
                return False
            
            # Kontrola veľkosti súboru
            content_length = int(response.headers.get('Content-Length', 0))
            if content_length > self.config['MAX_FILE_SIZE']:
                logger.warning(f"⚠️ Súbor príliš veľký: {content_length} bytes")
                return False
            
            # Ulož súbor
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            # Optimalizácia obrázka
            if self.config['OPTIMIZE_IMAGES']:
                self._optimize_image(save_path)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Chyba pri sťahovaní {image_url}: {e}")
            return False
    
    def _optimize_image(self, image_path: Path):
        """Optimalizuje obrázok"""
        try:
            from PIL import Image
            
            with Image.open(image_path) as img:
                # Zmenší ak je veľký
                max_size = self.config['THUMBNAIL_SIZE']
                if img.width > max_size[0] or img.height > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(
                        image_path, 
                        'JPEG', 
                        quality=self.config['QUALITY'], 
                        optimize=True
                    )
                    logger.debug(f"🔧 Obrázok optimalizovaný: {image_path.name}")
                    
        except ImportError:
            logger.warning("⚠️ PIL nie je nainštalované, preskakujem optimalizáciu")
        except Exception as e:
            logger.warning(f"⚠️ Chyba pri optimalizácii obrázka: {e}")

