from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
import os
from div_scripts.scrapers import mlp_scraper


class Command(BaseCommand):
    help = "Scrapuje MLP e-knihy (volně ke stažení) a ukládá průběžně do JSONL."

    def add_arguments(self, parser: CommandParser):
        default_dir = getattr(settings, "MEDIA_ROOT", settings.BASE_DIR)
        parser.add_argument("--out-jsonl",
                            default=os.path.join(default_dir, "mlp_eknihy.jsonl"),
                            help="Cesta k NDJSON (JSON Lines) souboru.")
        parser.add_argument("--limit", type=int, default=None, help="Omez počet záznamů (pro test).")
        parser.add_argument("--sleep", type=float, default=0.5, help="Prodleva mezi záznamy.")
        parser.add_argument("--no-resume", action="store_true",
                            help="Nepokračovat v existujícím souboru; zpracovat vše znovu.")
        parser.add_argument("--final-json", default=None,
                            help="Volitelné: po skončení vyrob i finální JSON pole.")
        parser.add_argument("--finalize-only", action="store_true",
                            help="Přeskočí scraping a převede jsonl -> json.")

    def handle(self, *args, **options):
        out_jsonl = options["out_jsonl"]
        final_json = options["final_json"]

        if options.get("finalize_only"):
            if final_json is None:
                base, _ = os.path.splitext(out_jsonl)
                final_json = base + ".json"
            mlp_scraper.finalize_json_from_jsonl(out_jsonl, final_json)
            self.stdout.write(self.style.SUCCESS(f"Finální JSON → {final_json}"))
            return
        
        
        out_jsonl = options["out_jsonl"]
        limit = options["limit"]
        sleep_between = options["sleep"]
        resume = not options["no_resume"]
        final_json = options["final_json"]

        self.stdout.write(self.style.NOTICE(f"Ukládám do: {out_jsonl} (resume={resume})"))
        mlp_scraper.scrape_all(
            out_jsonl=out_jsonl,
            limit=limit,
            sleep_between=sleep_between,
            resume=resume,
            logger=self.stdout.write,  # hezký logging do konzole
        )

        if final_json:
            mlp_scraper.finalize_json_from_jsonl(out_jsonl, final_json)
            self.stdout.write(self.style.SUCCESS(f"Finální JSON → {final_json}"))
        else:
            self.stdout.write(self.style.SUCCESS("Hotovo."))
