DOBROVSKY_BASE_CONFIG = {
    'BASE_URL': 'https://www.knihydobrovsky.cz',
    'API_URL': 'https://www.knihydobrovsky.cz/api/books',
    'CATEGORY_URL': 'https://www.knihydobrovsky.cz/knihy',
}

DOBROVSKY_SCRAPING_CONFIG = {
    'REQUEST_DELAY': 1.5,
    'MAX_RETRIES': 3,
    'TIMEOUT': 10,
    'BATCH_SIZE': 50,
}

DOBROVSKY_LANGUAGE_MAPPING = {
    'čeština': 'cs',
    'angličtina': 'en',
}

DOBROVSKY_GENRE_MAPPING = {
    'fantasy': 'Fantasy',
    'sci-fi': 'Science Fiction',
}

DOBROVSKY_SPECIFIC = {
    'EXTERNAL_ID_PREFIX': 'D-',
    'MIN_PRICE': 0,
    'MAX_PRICE': 10000,
}
