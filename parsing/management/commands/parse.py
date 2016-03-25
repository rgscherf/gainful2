from parsing.parsinglib import org_handler
from django.core.management.base import BaseCommand

orgs = org_handler.current_orgs

class Command(BaseCommand):
    def handle(self, *args, **options):
        org_handler.find_jobs()
