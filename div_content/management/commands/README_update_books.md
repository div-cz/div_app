# Update Books Command - Dokumentace

## Přehled

Management command `update_books` automaticky stahuje a aktualizuje knihy z Knihy Dobrovský a ukládá je do databáze s evidencí v tabulce `BookSource`.

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

## Jak to funguje

### 1. Scraping z Dobrovského

Command používá `DobrovskyScr` (`div_content/utils/dobrovsky_scraper.py`) pro stahování knih z https://www.knihydobrovsky.cz/knihy

Extrahuje:
- **External ID** - číslo z URL (např. `647575993` z `kniha/pod-letni-oblohou-647575993`)
- **Název knihy** - čistí suffix "Název" (např. "Pod letní oblohou Název" → "Pod letní oblohou")
- **Autor**
- **URL**
- Cenu (volitelně)
- Obrázek (volitelně)

### 2. Ukládání do databáze

Command používá `BookSourceService` (`div_content/utils/book_service.py`) pro:

#### BookSource tabulka
Každá kniha z Dobrovského se ukládá do `BookSource`:
```sql
BookSourceID    -- AutoField PK
BookID          -- FK na Book (může být NULL pokud se nepodaří spárovat)
SourceType      -- 'DOBROVSKY'
ExternalID      -- ID z Dobrovského (např. '647575993')
ExternalTitle   -- Původní název z Dobrovského
ExternalAuthors -- Autoři z Dobrovského
ExternalURL     -- URL na Dobrovském
CreatedAt       -- Timestamp vytvoření
```

**Unique constraint**: `(SourceType, ExternalID)` - zabraňuje duplicitám

#### Párování s Book tabulkou

Service se pokouší spárovat knihu s existující v `Book` tabulce podle:
- **Název + Autor** (unikátní kombinace)
- Hledá v `TitleCZ` nebo `Title` (case insensitive)
- Porovnává s `Author` (case insensitive)

**Pokud kniha existuje:**
- Spáruje `BookSource.BookID` s existujícím `Book.BookID`
- Nepřidává duplicitu do `Book`

**Pokud kniha neexistuje:**
- Vytvoří nový záznam v `Book`:
  - `title` a `titlecz` - vyčištěný název
  - `author` - jméno autora
  - `url` - jedinečné URL (podle pravidla níže)
  - `sourcetype` = 'DOBROVSKY'
  - `sourceid` = Externí ID
  - `divrating` = 50 (novinky mají rating 50)
  - `language` = 'cs'
  - `img` = 'noimg.png'

### 3. Generování URL pro knihy

Pravidlo pro `Book.url`:
1. **První pokus**: `nazev-knihy` (slugifikovaný název)
2. **Pokud existuje**: `nazev-knihy-autor` (název + autor)
3. **Pokud i to existuje**: `nazev-knihy-autor-2` (s číslem)

Příklad:
- "Pod letní oblohou" → `pod-letni-oblohou`
- Další s názvem "Pod letní oblohou", autor "Jana Nováková" → `pod-letni-oblohou-jana-novakova`

### 4. Prevence duplicit

- **BookSource**: Unique constraint na `(SourceType, ExternalID)` - nemůže existovat více záznamů se stejným External ID
- **Při běhu**: Command kontroluje existenci před vytvořením:
  - Pokud `BookSource` záznam existuje → `skipped` (nebo `updated` s `--force-update`)
  - Pokud Book existuje → spáruje místo vytvoření duplicity

## Výstup

```
============================================================
  AKTUALIZACE KNIH Z DOBROVSKÉHO (PRODUCTION 🚀)
============================================================
📋 Parametry:
   • Limit: 200 knih
   • Force update: Ne
   • Dry run: Ne

📡 KROK 1: Scraping Dobrovského...
✅ Načteno 24 knih

💾 KROK 2: Ukládání do databáze...

============================================================
📊 SOUHRN AKTUALIZACE
============================================================

⏱️  Čas běhu: 15.2s

📚 BOOK SOURCE:
   • Zpracováno: 24
   • Vytvořeno: 12
   • Aktualizováno: 0
   • Přeskočeno: 12
   • Chyby: 0

📖 KNIHY:
   • Nově vytvořeno: 8
   • Spárováno existujících: 4

✅ ÚSPĚŠNĚ DOKONČENO
🎉 Úspěšně zpracováno 12 záznamů v BookSource!

💡 DOPORUČENÍ:
   ✨ Všechno proběhlo hladce! Můžete zvýšit --limit pro více knih
============================================================
```

## Statistiky

| Pole | Popis |
|------|-------|
| **Zpracováno** | Celkový počet knih ze scrapingu |
| **Vytvořeno** | Nové záznamy v BookSource |
| **Aktualizováno** | Existující záznamy v BookSource (jen s --force-update) |
| **Přeskočeno** | Záznamy které už existují v BookSource |
| **Chyby** | Počet chyb při zpracování |
| **Nově vytvořeno** | Nové knihy v Book tabulce |
| **Spárováno existujících** | Knihy které už existovaly v Book |

## Týdenní spouštění

Pro automatické týdenní spouštění nastavte cron job:

```bash
# Každou neděli v 3:00 ráno
0 3 * * 0 cd /div_app && python manage.py update_books --limit=200
```

Nebo použijte Django Celery Beat pro periodické tasky.

## Troubleshooting

### Žádná data se neukládají do DB
- **Původní problém**: Command importoval z neexistujícího balíčku `div_management`
- **Řešení**: Nová implementace s `dobrovsky_scraper.py` a `book_service.py`

### Hodně duplicit
- Použijte `--force-update` pro aktualizaci existujících záznamů
- Zkontrolujte unikátní constraint v BookSource

### Scraping selhává s 403 Forbidden
- **Běžný problém**: Dobrovský blokuje některé IP adresy/datacentra
- **Řešení**: Command musí běžet z prostředí které Dobrovský neblokuje
- **Alternativa**: Použít Selenium/Playwright pro simulaci reálného prohlížeče
- Zkontrolujte dostupnost https://www.knihydobrovsky.cz
- Možná se změnila struktura HTML (aktualizujte selektory ve scraperu)

### Knihy se nespárují správně
- Zkontrolujte log - `logger.info()` ukazuje zda byla kniha nalezena
- Možná rozdíl v názvech (extra mezery, diakritika, etc.)
- Zvažte vylepšení fuzzy matchingu

## Struktura souborů

```
div_content/
├── management/
│   └── commands/
│       ├── update_books.py          # Management command
│       └── README_update_books.md   # Tato dokumentace
├── utils/
│   ├── dobrovsky_scraper.py         # Scraper pro Dobrovského
│   └── book_service.py              # Service pro správu BookSource
└── models.py                        # Modely Book, Booksource
```

## TODO / Budoucí vylepšení

- [ ] Implementovat plnění `BookWriters` (BookID + AuthorID)
- [ ] Implementovat plnění `BookGenre` (BookID + GenreID)
- [ ] Implementovat plnění `BookKeywords` (BookID + MetaKeywords)
- [ ] Stahování obrázků z Dobrovského
- [ ] Lepší fuzzy matching pro párování knih
- [ ] Support pro více autorů
- [ ] Parsing ISBN z detailu knihy
- [ ] Integrace s dalšími zdroji (CBDB, Databáze knih)

## Kontakt

Pro otázky nebo bug reporty kontaktujte vývojový tým.
