import requests
from bs4 import BeautifulSoup
from parsing.parsinglib import organizations
from django.core.management.base import BaseCommand

orgs = [ organizations.Victoria()
          , organizations.Toronto()
#         , organizations.Hamilton()
#         , organizations.Mississauga()
#         , organizations.CRD()
#         , organizations.OPS()
#         , organizations.BCPS()
#         , organizations.CivicInfo()
#         , organizations.CivicInfo_North_Central()
#         , organizations.CivicInfo_Lower_Mainland()
#         , organizations.AMCTO()
        ]

class Command(BaseCommand):
    def handle(self, *args, **options):
        for o in orgs:
            r = requests.get(o.request_url)
            soup = BeautifulSoup(r.text, "html5lib")
            o.parse(soup)
