from django.core.management.base import BaseCommand
from django.utils import timezone
from div_content.models import Userdivcoins

class Command(BaseCommand):
    help = "Resetuje DIVcoiny (weekly, monthly, yearly) podle parametru"

    def add_arguments(self, parser):
        parser.add_argument(
            "--weekly",
            action="store_true",
            help="Resetuje týdenní DIVcoiny",
        )
        parser.add_argument(
            "--monthly",
            action="store_true",
            help="Resetuje měsíční DIVcoiny",
        )
        parser.add_argument(
            "--yearly",
            action="store_true",
            help="Resetuje roční DIVcoiny",
        )

    def handle(self, *args, **options):
        now = timezone.now().date()

        if options["weekly"]:
            updated = Userdivcoins.objects.update(
                weeklydivcoins=0, lastupdated=now
            )
            self.stdout.write(self.style.SUCCESS(f"Weekly reset hotovo ({updated} řádků)"))

        elif options["monthly"]:
            updated = Userdivcoins.objects.update(
                monthlydivcoins=0, lastupdated=now
            )
            self.stdout.write(self.style.SUCCESS(f"Monthly reset hotovo ({updated} řádků)"))

        elif options["yearly"]:
            updated = Userdivcoins.objects.update(
                yearlydivcoins=0, lastupdated=now
            )
            self.stdout.write(self.style.SUCCESS(f"Yearly reset hotovo ({updated} řádků)"))

        else:
            self.stdout.write(self.style.ERROR("Musíš zadat --weekly nebo --monthly nebo --yearly"))
