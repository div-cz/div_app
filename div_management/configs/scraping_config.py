UNIVERSAL_SCRAPING_CONFIG = {
    'REQUEST_DELAY': 1.0,
    'MAX_RETRIES': 3,
    'TIMEOUT': 10,
    'HEADERS': {
        'User-Agent': 'Kultura Bot',
        'Accept': 'application/json, text/html',
    },
    'ERROR_HANDLING': {
        'EXPONENTIAL_BACKOFF': True,
        'MAX_BACKOFF_TIME': 60,
    }
}