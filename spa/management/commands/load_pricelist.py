"""Load the official Oasis service price list (idempotent).

Run:  python manage.py load_pricelist
"""
from django.core.management.base import BaseCommand

from spa.pricelist import load_services


class Command(BaseCommand):
    help = "Load/refresh the official service catalogue and prices."

    def handle(self, *args, **opts):
        services = load_services()
        self.stdout.write(self.style.SUCCESS(
            f'Loaded {len(services)} services from the official price list.'))
