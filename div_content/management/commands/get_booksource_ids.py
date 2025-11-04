from django.core.management.base import BaseCommand
from div_content.models import Booksource


class Command(BaseCommand):
    help = "Gets all IDs from Booksource table and export them into TXT file."

    def handle(self, *args, **options):
        existing_ids = set(
            Booksource.objects.filter(sourcetype="CBDB").values_list("externalid", flat=True)
        )
        total = len(existing_ids)
        with open("div_app/cbdb_ids.txt", "w", encoding="utf-8") as f:
            for id in existing_ids:
                f.write(str(id) + "\n")
        
        self.stdout.write(
            self.style.SUCCESS('Successfully processed "%s" IDs.' % total)
        )