# div_content/management/commands/update_books.py

"""
Django Management Command pro aktualizaci knih z Knihy Dobrovský

Použití:
    python manage.py update_books                    # Standardní běh (200 knih)
    python manage.py update_books --limit=100        # Pouze 100 knih
    python manage.py update_books --force-update     # Aktualizuj i existující
    python manage.py update_books --dry-run          # Test bez ukládání
    python manage.py update_books --test-single      # Test s 1 knihou
"""

import logging
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from div_content.utils.dobrovsky_scraper import scrape_dobrovsky_books
from div_content.utils.book_service import BookSourceService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Aktualizuje knihy z Knihy Dobrovský a ukládá do BookSource'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=200,
            help='Počet knih na zpracování (default: 200)'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Testovací režim bez ukládání do databázy'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Detailní výstup pro debugging'
        )

        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Vynúti aktualizaci i existujících knih'
        )

        parser.add_argument(
            '--test-single',
            action='store_true',
            help='Test s jednou knihou'
        )

    def handle(self, *args, **options):
        """Hlavní metóda management commandu"""

        start_time = datetime.now()

        # Nastavení loggingu
        if options['verbose']:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        # Nastavení
        dry_run = options['dry_run']
        verbose = options['verbose']
        force_update = options['force_update']
        limit = options['limit']

        # Test mode
        if options['test_single']:
            limit = 1
            verbose = True

        # Úvodná správa
        mode = "DRY RUN 🧪" if dry_run else "PRODUCTION 🚀"
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*60}\n"
            f"  AKTUALIZACE KNIH Z DOBROVSKÉHO ({mode})\n"
            f"{'='*60}"
        ))
        self.stdout.write(f"📋 Parametry:")
        self.stdout.write(f"   • Limit: {limit} knih")
        self.stdout.write(f"   • Force update: {'Ano' if force_update else 'Ne'}")
        self.stdout.write(f"   • Dry run: {'Ano' if dry_run else 'Ne'}\n")

        try:
            # KROK 1: Scraping z Dobrovského
            self.stdout.write(self.style.HTTP_INFO("📡 KROK 1: Scraping Dobrovského..."))

            books = scrape_dobrovsky_books(limit=limit)

            if not books:
                self.stdout.write(self.style.WARNING("⚠️ Žádné knihy nenalezeny!"))
                return

            self.stdout.write(self.style.SUCCESS(f"✅ Načteno {len(books)} knih\n"))

            # KROK 2: Zpracování a ukládání do DB
            self.stdout.write(self.style.HTTP_INFO("💾 KROK 2: Ukládání do databáze..."))

            service = BookSourceService()

            with transaction.atomic():
                if dry_run:
                    # V dry-run režimu rollback transakce
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("⚠️ DRY RUN - změny nebudou uloženy\n"))

                # Zpracuj každou knihu
                for idx, book in enumerate(books, 1):
                    if verbose:
                        self.stdout.write(f"[{idx}/{len(books)}] Zpracovávám: {book.title}")

                    success, msg = service.process_dobrovsky_book(book, force_update=force_update)

                    if verbose and not success:
                        self.stdout.write(self.style.ERROR(f"   ❌ Chyba: {msg}"))

                # Získej statistiky
                stats = service.get_stats()

            # KROK 3: Výsledný report
            self._print_summary(stats, start_time, dry_run)

            # Log finálního stavu
            logger.info(f"✅ Command dokončený: {stats}")

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n⚠️ Aktualizace přerušena uživatelem"))
            logger.warning("Command přerušený uživatelem")

        except Exception as e:
            error_msg = f"❌ Kritická chyba: {e}"
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg, exc_info=True)
            raise CommandError(f"Command selhal: {e}")

    def _print_summary(self, stats: dict, start_time: datetime, dry_run: bool):
        """Vypíše souhrn výsledků"""

        duration = datetime.now() - start_time

        # Hlavní souhrn
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS("📊 SOUHRN AKTUALIZACE"))
        self.stdout.write("="*60)

        # Statistiky
        self.stdout.write(f"\n⏱️  Čas běhu: {duration.total_seconds():.1f}s")
        self.stdout.write(f"\n📚 BOOK SOURCE:")
        self.stdout.write(f"   • Zpracováno: {stats['processed']}")
        self.stdout.write(f"   • Vytvořeno: {stats['created']}")
        self.stdout.write(f"   • Aktualizováno: {stats['updated']}")
        self.stdout.write(f"   • Přeskočeno: {stats['skipped']}")
        self.stdout.write(f"   • Chyby: {stats['errors']}")

        self.stdout.write(f"\n📖 KNIHY:")
        self.stdout.write(f"   • Nově vytvořeno: {stats['books_created']}")
        self.stdout.write(f"   • Spárováno existujících: {stats['books_matched']}")

        # Farebný souhrn
        total_success = stats['created'] + stats['updated']
        if stats['errors'] == 0:
            status_style = self.style.SUCCESS
            status_msg = "✅ ÚSPĚŠNĚ DOKONČENO"
        elif stats['errors'] < stats['processed'] / 2:
            status_style = self.style.WARNING
            status_msg = "⚠️ DOKONČENO S CHYBAMI"
        else:
            status_style = self.style.ERROR
            status_msg = "❌ SELHALO"

        self.stdout.write("\n" + status_style(status_msg))

        # Dodatočné informace
        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\n🧪 DRY RUN - Žádné změny nebyly uloženy do databáze!"
            ))

        if total_success > 0 and not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\n🎉 Úspěšně zpracováno {total_success} záznamů v BookSource!"
            ))

        if stats['errors'] > 0:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️ Zkontrolujte logy pro {stats['errors']} chyb"
            ))

        # Odporučení
        self._print_recommendations(stats)

        self.stdout.write(f"\n{'='*60}\n")

    def _print_recommendations(self, stats: dict):
        """Vypíše odporučení na základě výsledků"""

        recommendations = []

        # Pokud bylo hodně chyb
        if stats['errors'] > stats['processed'] * 0.1:  # Více než 10% chyb
            recommendations.append(
                "🔧 Hodně chyb - zkontrolujte dostupnost serveru Dobrovského"
            )

        # Pokud bylo hodně přeskočených
        if stats['skipped'] > stats['processed'] * 0.5:  # Více než 50% přeskočených
            recommendations.append(
                "📈 Hodně duplicit - zvažte --force-update pro aktualizaci"
            )

        # Pokud nebyly vytvořeny žádné záznamy
        if stats['created'] == 0 and stats['updated'] == 0:
            recommendations.append(
                "📚 Žádné nové záznamy - možná zvyšte --limit nebo zkontrolujte zdroj"
            )

        # Pokud bylo všechno v pořádku
        if not recommendations and stats['processed'] > 0:
            recommendations.append(
                "✨ Všechno proběhlo hladce! Můžete zvýšit --limit pro více knih"
            )

        if recommendations:
            self.stdout.write("\n💡 DOPORUČENÍ:")
            for rec in recommendations:
                self.stdout.write(f"   {rec}")
