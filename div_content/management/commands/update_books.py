# div_content/management/commands/update_books.py

"""Django Management Command pre aktualizáciu kníh z Dobrovský"""

# python manage.py update_books --limit=100

import logging
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Import z našej div_management štruktúry
from div_management.books.book_update_service import BookUpdateService
from div_management.shared.universal_logger import setup_logging, get_logger
from div_management.configs.paths_config import ensure_directories

# Import pre BookSource
from div_content.models import Book, Booksource


class Command(BaseCommand):
    help = 'Aktualizuje knihy z Knihy Dobrovský a ukládá do BookSource'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=200,
            help='Počet kníh na spracovanie (default: 200)'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Testovací režim bez ukladania do databázy'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Detailný výstup pre debugging'
        )

        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Vynúti aktualizáciu aj existujúcich kníh'
        )

        parser.add_argument(
            '--test-single',
            action='store_true',
            help='Test s jednou knihou'
        )

    def handle(self, *args, **options):
        """Hlavná metóda management commandu"""

        start_time = datetime.now()

        # Zabezpeč existenciu adresárov
        ensure_directories()

        # Setup logovania
        setup_logging(verbose=options['verbose'])
        logger = get_logger('books', 'books_update')

        # Nastavenia
        dry_run = options['dry_run']
        verbose = options['verbose']
        force_update = options['force_update']
        limit = options['limit']

        # Test mode
        if options['test_single']:
            limit = 1
            verbose = True

        # Úvodná správa
        mode = "DRY RUN" if dry_run else "PRODUCTION"
        self.stdout.write(
            self.style.SUCCESS(
                f"🚀 Spúšťam aktualizáciu kníh z Dobrovský ({mode})"
            )
        )
        self.stdout.write(f"📋 Parametre: limit={limit}, force_update={force_update}")

        try:
            # Vytvor service
            update_service = BookUpdateService(dry_run=dry_run)

            # Spusti aktualizáciu
            with transaction.atomic():
                if dry_run:
                    # V dry-run režime nevykonávaj skutočné transakcie
                    transaction.set_rollback(True)

                result = update_service.update_books_from_dobrovsky(
                    limit=limit,
                    force_update=force_update
                )

                # 🆕 NOVÉ: Synchronizuj BookSource záznamy
                if not dry_run and result['processed'] > 0:
                    self._sync_book_sources(logger)

            # Výsledný report
            self._print_summary(result, start_time)

            # Log finálneho stavu
            logger.info(f"✅ Command dokončený úspešne: {result}")

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING("⚠️ Aktualizácia prerušená používateľom")
            )
            logger.warning("Command prerušený používateľom")

        except Exception as e:
            error_msg = f"❌ Kritická chyba: {e}"
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg, exc_info=True)
            raise CommandError(f"Command zlyhal: {e}")

    def _sync_book_sources(self, logger):
        """
        Synchronizuje BookSource záznamy pre knihy z Dobrovského

        Pre všetky knihy kde sourcetype='DOB' a sourceid existuje,
        vytvor/aktualizuj záznam v BookSource
        """
        logger.info("📊 Synchronizujem BookSource záznamy...")

        # Najdi všetky knihy z Dobrovského ktoré majú sourceid
        dob_books = Book.objects.filter(
            sourcetype='DOB',
            sourceid__isnull=False
        ).exclude(sourceid='')

        synced = 0
        created = 0
        updated = 0

        for book in dob_books:
            try:
                # Vytvor/aktualizuj BookSource záznam
                book_source, was_created = Booksource.objects.update_or_create(
                    sourcetype='DOBROVSKY',
                    externalid=str(book.sourceid),
                    defaults={
                        'bookid': book,
                        'externaltitle': book.titlecz or book.title,
                        'externalauthors': book.author,
                        'externalurl': f'https://www.knihydobrovsky.cz/kniha/{book.url}-{book.sourceid}',
                    }
                )

                if was_created:
                    created += 1
                    logger.debug(f"✨ BookSource vytvorený: {book.title} (ID: {book.sourceid})")
                else:
                    updated += 1
                    logger.debug(f"🔄 BookSource aktualizovaný: {book.title} (ID: {book.sourceid})")

                synced += 1

            except Exception as e:
                logger.warning(f"⚠️ Chyba pri sync BookSource pre {book.title}: {e}")
                continue

        logger.info(f"✅ BookSource sync: {synced} celkom ({created} nových, {updated} aktualizovaných)")
        self.stdout.write(f"📊 BookSource: {created} nových, {updated} aktualizovaných")

    def _print_summary(self, result: dict, start_time: datetime):
        """Vypíše súhrn výsledkov"""

        duration = datetime.now() - start_time

        # Hlavný súhrn
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📊 SÚHRN AKTUALIZÁCIE"))
        self.stdout.write("="*50)

        # Štatistiky
        stats_lines = [
            f"⏱️  Čas behu: {duration.total_seconds():.1f}s",
            f"📖 Spracované: {result['processed']}",
            f"✅ Vytvorené: {result['created']}",
            f"🔄 Aktualizované: {result['updated']}",
            f"⏭️  Preskočené: {result['skipped']}",
            f"❌ Chyby: {result['errors']}"
        ]

        for line in stats_lines:
            self.stdout.write(line)

        # Farebný súhrn
        total_success = result['created'] + result['updated']
        if result['errors'] == 0:
            status_style = self.style.SUCCESS
            status_msg = "✅ ÚSPEŠNE DOKONČENÉ"
        elif result['errors'] < result['processed'] / 2:
            status_style = self.style.WARNING
            status_msg = "⚠️ DOKONČENÉ S CHYBAMI"
        else:
            status_style = self.style.ERROR
            status_msg = "❌ ZLYHALO"

        self.stdout.write("\n" + status_style(status_msg))

        # Dodatočné informácie
        if total_success > 0:
            self.stdout.write(
                self.style.SUCCESS(f"🎉 Úspešne spracovaných {total_success} kníh!")
            )

        if result['errors'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ Skontrolujte logy pre {result['errors']} chýb"
                )
            )

        # Odporúčania
        self._print_recommendations(result)

        self.stdout.write("="*50 + "\n")

    def _print_recommendations(self, result: dict):
        """Vypíše odporúčania na základe výsledkov"""

        recommendations = []

        # Ak bolo veľa chýb
        if result['errors'] > result['processed'] * 0.1:  # Viac ako 10% chýb
            recommendations.append(
                "🔧 Veľa chýb - skontrolujte dostupnosť Dobrovský servera"
            )

        # Ak bolo veľa preskočených
        if result['skipped'] > result['processed'] * 0.5:  # Viac ako 50% preskočených
            recommendations.append(
                "📈 Veľa duplikátov - zvážte --force-update pre aktualizáciu"
            )

        # Ak bolo málo vytvorených
        if result['created'] == 0 and not result['updated']:
            recommendations.append(
                "📚 Žiadne nové knihy - možno zvýšte --limit alebo skontrolujte zdroj"
            )

        # Ak bolo všetko v poriadku
        if not recommendations and result['processed'] > 0:
            recommendations.append(
                "✨ Všetko prebehlo hladko! Môžete zvýšiť --limit pre viac kníh"
            )

        if recommendations:
            self.stdout.write("\n💡 ODPORÚČANIA:")
            for rec in recommendations:
                self.stdout.write(f"   {rec}")
