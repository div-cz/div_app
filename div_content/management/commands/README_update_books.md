# Update Books Command - Dokumentace

## Přehled

Management command `update_books` automaticky stahuje a aktualizuje knihy z Knihy Dobrovský pomocí **div_management** balíčku a eviduje je v tabulce `BookSource`.

## Použití

```bash
# Základní použití (200 knih)
python manage.py update_books

# S vlastním limitem
python manage.py update_books --limit=100

# Test bez ukládání do DB
python manage.py update_books --dry-run

# Aktualizace i existujících záznamů
python manage.py update_books --force-update

# Test s jednou knihou
python manage.py update_books --test-single

# Detailní výstup
python manage.py update_books --verbose
```

## Architektura

Command používá **div_management** balíček (gitignored složka s komplexní logikou):

```
div_management/
├── scraping/
│   └── dobrovsky_scraper.py    # Scraper parsující JSON z HTML atributů
├── books/
│   ├── book_update_service.py  # Hlavní service pro zpracování knih
│   ├── book_duplicate_service.py  # Detekce duplicit
│   ├── book_image_service.py   # Stahování obrázků
│   └── book_utils.py           # URL generování
├── shared/
│   ├── universal_db_helper.py  # DB helpers (autori, žánry)
│   └── universal_logger.py     # Logging
└── configs/
    └── paths_config.py         # Konfigurace cest
```

## Jak to funguje

### 1. Scraping z Dobrovského (div_management)

**DobroskyScraper** používá chytrý přístup - parsuje JSON data z HTML atributů místo HTML struktury:

```html
<li data-productinfo='{"id": 123, "name": "Kniha", "brand": "Autor"}'>
```

Extrahuje:
- **external_id** - ID produktu z Dobrovského
- **title** - název knihy
- **author_name** - autor
- **price** - cena
- **category** - kategorie/žánr
- **rating** - hodnocení

**Výhoda:** Mnohem spolehlivější než parsování HTML CSS tříd!

### 2. Zpracování knihy (BookUpdateService)

Pro každou knihu:

1. **Detekce duplicit** (`BookDuplicateService`):
   - Hledá podle `TitleCZ + Author`
   - Také kontroluje `external_id` v `sourceid`

2. **Vytvoření/aktualizace** v `Book` tabulce:
   - Vytvoří novou knihu pokud neexistuje
   - Aktualizuje existující pokud `--force-update`
   - Nastaví `sourcetype='DOB'` a `sourceid=external_id`

3. **Doplňující operace**:
   - Stažení obrázku (`BookImageService`)
   - Vytvoření autora (`get_or_create_author`)
   - Přiřazení žánru (`Bookgenre`)
   - Propojení autora (`Bookwriters`)

### 3. Synchronizace BookSource (NOVÉ)

Po zpracování všech knih command automaticky **synchronizuje BookSource**:

```python
def _sync_book_sources(self, logger):
    # Najde všechny knihy s sourcetype='DOB'
    dob_books = Book.objects.filter(sourcetype='DOB', sourceid__isnull=False)

    for book in dob_books:
        # Vytvoří/aktualizuje BookSource záznam
        Booksource.objects.update_or_create(
            sourcetype='DOBROVSKY',
            externalid=str(book.sourceid),
            defaults={
                'bookid': book,
                'externaltitle': book.titlecz or book.title,
                'externalauthors': book.author,
                'externalurl': f'https://www.knihydobrovsky.cz/kniha/{book.url}-{book.sourceid}',
            }
        )
```

**BookSource tabulka:**
```sql
BookSourceID     -- AutoField PK
BookID           -- FK na Book
SourceType       -- 'DOBROVSKY', 'CBDB', 'DB'
ExternalID       -- ID z externího zdroje
ExternalTitle    -- Původní název
ExternalAuthors  -- Autoři
ExternalURL      -- URL na externí zdroj
CreatedAt        -- Timestamp
```

**Unique constraint**: `(SourceType, ExternalID)` - zabraňuje duplicitám

### 4. Generování URL pro knihy

`BookURLGenerator` vytváří unikátní URL podle pravidel:
1. **První pokus**: `nazev-knihy`
2. **Pokud existuje**: `nazev-knihy-autor`
3. **Pokud i to existuje**: `nazev-knihy-autor-2`

## Výstup

```
🚀 Spúšťam aktualizáciu kníh z Dobrovský (PRODUCTION)
📋 Parametre: limit=200, force_update=False

==================================================
📊 SÚHRN AKTUALIZÁCIE
==================================================
⏱️  Čas behu: 15.2s
📖 Spracované: 24
✅ Vytvorené: 12
🔄 Aktualizované: 0
⏭️  Preskočené: 12
❌ Chyby: 0

📊 BookSource: 24 nových, 0 aktualizovaných

✅ ÚSPEŠNE DOKONČENÉ
🎉 Úspešne spracovaných 12 kníh!

💡 ODPORÚČANIA:
   ✨ Všetko prebehlo hladko! Môžete zvýšiť --limit pre viac kníh
==================================================
```

## Statistiky

| Pole | Popis |
|------|-------|
| **Zpracované** | Celkový počet knih ze scrapingu |
| **Vytvořené** | Nové knihy v Book tabulce |
| **Aktualizované** | Existující knihy aktualizované v Book |
| **Přeskočené** | Knihy které už existují (bez změn) |
| **Chyby** | Počet chyb při zpracování |
| **BookSource nových** | Nové záznamy v BookSource |
| **BookSource aktualizovaných** | Existující záznamy aktualizované |

## Týdenní spouštění

Pro automatické týdenní spouštění nastavte cron job:

```bash
# Každou neděli v 3:00 ráno
0 3 * * 0 cd /div_app && python manage.py update_books --limit=200
```

Nebo použijte Django Celery Beat pro periodické tasky.

## Databázové tabulky

### Book (hlavní)
- `sourcetype='DOB'` - typ zdroje
- `sourceid` - ExternalID z Dobrovského
- `title`, `titlecz`, `author` - základní data
- `url` - unikátní URL
- `divrating` - rating (nově 0, lze nastavit ručně)

### BookSource (evidence externích zdrojů)
- `sourcetype='DOBROVSKY'` - typ zdroje
- `externalid` - ID z Dobrovského
- `bookid` - FK na Book
- `externaltitle`, `externalauthors` - původní data
- `externalurl` - odkaz na Dobrovského

### Bookwriters (propojení autora)
- `book_id` - FK na Book
- `author_id` - FK na Bookauthor

### Bookgenre (propojení žánru)
- `bookid` - FK na Book
- `genreid` - FK na Metagenre

## Troubleshooting

### Žádná data se neukládají do DB
- Zkontroluj že `div_management/` složka existuje
- Zkontroluj že není v dry-run módu
- Podívej se do logů: `/div_app/data/div_management/logs/`

### Hodně duplicit
- Použij `--force-update` pro aktualizaci existujících záznamů
- Zkontroluj unique constraint v BookSource

### Scraping selhává
- **Běžný problém**: Dobrovský může změnit HTML strukturu
- Zkontroluj že `div_management/scraping/dobrovsky_scraper.py` parsuje správné atributy
- Podívej se na HTML: `https://www.knihydobrovsky.cz/knihy?sort=1`
- Hledej `<li data-productinfo=` elementy

### Knihy se nespárují správně
- Zkontroluj log - `BookDuplicateService` ukazuje zda byla kniha nalezena
- Možná rozdíl v názvech (extra mezery, diakritika, etc.)
- Zvažte vylepšení fuzzy matchingu v `book_duplicate_service.py`

### Import error: No module named 'div_management'
- **Problém**: `div_management/` složka chybí nebo není v PYTHONPATH
- **Řešení**: Ujisti se že běžíš command z `/div_app` root
- Zkontroluj že složka existuje: `ls -la /div_app/div_management`

## Struktura souborů

```
div_app/
├── div_management/              # Gitignored složka s logikou
│   ├── scraping/
│   │   └── dobrovsky_scraper.py
│   ├── books/
│   │   ├── book_update_service.py
│   │   ├── book_duplicate_service.py
│   │   ├── book_image_service.py
│   │   └── book_utils.py
│   ├── shared/
│   │   ├── universal_db_helper.py
│   │   └── universal_logger.py
│   └── configs/
│       └── paths_config.py
│
├── div_content/
│   ├── management/
│   │   └── commands/
│   │       ├── update_books.py           # Management command
│   │       └── README_update_books.md    # Tato dokumentace
│   └── models.py                         # Book, Booksource
│
└── data/                                 # Data a logy
    └── div_management/
        └── logs/
            └── books_update.log
```

## TODO / Budoucí vylepšení

- [ ] Automatické nastavení `DIVRating=50` pro novinky
- [ ] Support pro více stránek (paginace)
- [ ] Lepší fuzzy matching pro párování knih
- [ ] Support pro více autorů na jedné knize
- [ ] Parsing ISBN z detailu knihy
- [ ] Integrace s dalšími zdroji (CBDB, Databáze knih)
- [ ] Webhook notifikace při nových knihách

## Kontakt

Pro otázky nebo bug reporty kontaktujte vývojový tým.
