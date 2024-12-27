import os
import logging
import datetime
from typing import Optional


def setup_logging(log_name_prefix: str) -> None:
    """
    Sets up logging configuration.

    This function creates a log directory named after the log_name_prefix within 'div_scripts',
    initializes a log file with a timestamped filename, and configures the logging settings.

    Args:
        log_name_prefix (str): Prefix for the log filename and the log directory name.

    Returns:
        None
    """
    # Vytvoření časového razítka pro log soubor
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M-%S")

    # Definování plné cesty k log adresáři (bez 'movies')
    full_log_dir = os.path.join("div_scripts", log_name_prefix)

    # Vytvoření adresáře, pokud neexistuje
    os.makedirs(full_log_dir, exist_ok=True)

    # Definování názvu log souboru
    log_filename = os.path.join(full_log_dir, f"{log_name_prefix}_{current_datetime}.log")

    # Konfigurace základního nastavení logování
    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Záznam inicializační zprávy
    logging.info(f"Logging initialized for {log_name_prefix} at {current_datetime}")
