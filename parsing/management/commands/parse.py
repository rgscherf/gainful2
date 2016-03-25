import requests
from bs4 import BeautifulSoup
from parsing.parsinglib import org_handler
from django.core.management.base import BaseCommand

orgs = org_handler.current_orgs

class Command(BaseCommand):
    def handle(self, *args, **options):
        for o in orgs:
            r = requests.get(o.request_url)
            soup = BeautifulSoup(r.text, "html5lib")
            o.parse(soup)
