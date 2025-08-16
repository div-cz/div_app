# -------------------------------------------------------------------
#             div_management/shared/universal_logger.py
# -------------------------------------------------------------------

"""Univerzálne logovanie pre div_management"""

import logging
import logging.handlers
from pathlib import Path

# NOVÁ CESTA
LOG_DIR = Path('/var/www/magic.div.cz/data/div_management/logs')

def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def get_logger(name: str, log_file: str = None):
    logger = logging.getLogger(f'div_management.{name}')
    
    if logger.handlers:
        return logger
    
    if log_file:
        # Zabezpeč že adresár existuje
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        file_path = LOG_DIR / f'{log_file}.log'
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(file_handler)
        except PermissionError:
            print(f"⚠️ Nemôžem zapisovať do {file_path}, pokračujem bez file loggingu")
    
    return logger


