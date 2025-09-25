from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = "Zjistí typy formátů dostupných MLP eknih."

    def handle(self, *args, **options):
        with open("img/mlp_eknihy.json", "r", encoding="utf-8") as f:
            data = json.load(f)

            formats = set()
        counter = 0
        for book in data:
            for dl in book.get("downloads", []):
                fmt = dl.get("format")
                if fmt:
                    formats.add(fmt.lower())
            counter += 1
            print(f"[OK] záznam {counter}", flush=True)

        print(f"Nalezené formáty ({len(formats)}): {sorted(formats)}", flush=True)

