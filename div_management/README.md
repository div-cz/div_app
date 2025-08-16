# ================================================================

# README.md pre div_management

"""
# DIV Management System

Systém pre automatickú správu obsahu (knihy, filmy, hry) s podporou web scrapingu.

## 📁 Štruktúra

```
div_management/
├── books/                     # Správa kníh
│   ├── book_update_service.py    # Hlavná logika
│   ├── book_duplicate_service.py # Duplikáty (TitleCZ + Author)
│   ├── book_image_service.py     # Obrázky
│   └── book_utils.py            # Pomocné funkcie
├── scraping/                  # Web scraping
│   ├── base_scraper.py          # Abstraktná trieda
│   ├── dobrovsky_scraper.py     # Dobrovský scraper
│   └── dobrovsky_normalizer.py  # Normalizácia dát
├── shared/                    # Spoločné nástroje
│   ├── universal_logger.py      # Logovanie
│   ├── universal_url_cleaner.py # URL čistenie
│   ├── universal_validators.py  # Validácie
│   └── universal_db_helper.py   # DB operácie
├── configs/                   # Konfigurácie
│   ├── global_config.py         # Globálne nastavenia
│   ├── dobrovsky_config.py      # Dobrovský nastavenia
│   └── books_config.py          # Knihy nastavenia
└── logs/                      # Log súbory
    ├── books_update.log
    ├── books_duplicates.log
    └── dobrovsky_scraping.log
```

## 🚀 Použitie

### Základné spustenie
```bash
python manage.py update_books --limit 100
```

### Testovací režim
```bash
python manage.py update_books --dry-run --verbose --limit 5
```

### Aktualizácia existujúcich
```bash
python manage.py update_books --force-update --limit 50
```

### Test jednej knihy
```bash
python manage.py update_books --test-single --verbose
```

## 🔧 Konfigurácia

### Dobrovský nastavenia
Upraviť `div_management/configs/dobrovsky_config.py`:

```python
DOBROVSKY_SCRAPING_CONFIG = {
    'REQUEST_DELAY': 1.5,        # Pauza medzi requestami
    'MAX_RETRIES': 3,            # Počet pokusov
    'BATCH_SIZE': 50,            # Veľkosť batchu
}
```

### Obrázky kníh
Upraviť `div_management/configs/books_config.py`:

```python
BOOKS_IMAGE_CONFIG = {
    'BASE_PATH': '/data/shared/kniha',
    'MAX_IMAGES_PER_FOLDER': 5000,
    'OPTIMIZE_IMAGES': True,
}
```

## 📊 Logika duplikátov

**Pravidlo**: `TitleCZ + Author` = unikátna dvojica

1. **Hľadanie duplikátu**: Kniha je duplikát ak má rovnaký názov a autora
2. **Aktualizácia**: Doplnia sa iba CHYBĚJÍCÍ polia
3. **Konflikty**: Logujú sa rozdiely v existujúcich poliach

### Príklad:
```
Existujúca: "Harry Potter" + "J.K. Rowling"
- year: NULL → doplň 1997 ✅
- pages: 300 → ponechaj, ale loguj konflikt ak scraper má 320 ⚠️
- description: NULL → doplň scraper data ✅
```

## 🤖 Cron job

### Denná aktualizácia
```bash
# /etc/crontab
0 2 * * * www-data cd /var/www/magic.div.cz && python manage.py update_books --limit 200 >> /var/log/div_books.log 2>&1
```

### Týždenná force aktualizácia
```bash
0 3 * * 0 www-data cd /var/www/magic.div.cz && python manage.py update_books --force-update --limit 1000
```

## 📈 Monitorovanie

### Sledovanie logov
```bash
# Real-time sledovanie
tail -f div_management/logs/books_update.log

# Posledné behy
grep "Dokončené" div_management/logs/books_update.log | tail -5

# Chyby za dnes
grep "ERROR" div_management/logs/books_update.log | grep $(date +%Y-%m-%d)
```

### Štatistiky z logu
```bash
# Počet spracovaných kníh dnes
grep "spracovaných" div_management/logs/books_update.log | grep $(date +%Y-%m-%d) | tail -1

# Duplikáty za posledný týždeň
grep "Nájdená duplicita" div_management/logs/books_duplicates.log | grep -c $(date -d '7 days ago' +%Y-%m)
```

## 🛠️ Rozšírenie pre filmy

Pre pridanie filmov:

1. **Vytvor movies modul**:
```bash
mkdir div_management/movies
```

2. **Skopíruj štruktúru z books**:
```python
# div_management/movies/movie_update_service.py
# div_management/scraping/csfd_scraper.py
```

3. **Vytvor management command**:
```python
# div_content/management/commands/update_movies.py
from div_management.movies import MovieUpdateService
```

## 🐛 Troubleshooting

### Časté problémy

1. **Chyba pri sťahovaní obrázkov**
   - Skontroluj permissions na `/data/shared/kniha`
   - Skontroluj dostupnosť Dobrovský servera

2. **Príliš veľa duplikátov**
   - Použij `--force-update` pre aktualizáciu
   - Skontroluj logiku v `book_duplicate_service.py`

3. **Pomalé spracovanie**
   - Zvýš `REQUEST_DELAY` v konfigurácii
   - Zníž `--limit` parameter

### Debug režim
```bash
python manage.py update_books --test-single --verbose
```

Zobrazí detailný priebeh spracovania jednej knihy.
"""