import os
import requests
from bs4 import BeautifulSoup
from .parsinglib import organizations

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gainful2.settings")

orgs = [ organizations.Victoria()
#           organizations.Toronto()
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

def main():
    for o in orgs:
        r = requests.get(o.request_url)
        soup = BeautifulSoup(r.text, "html5lib")
        o.parse(soup)

if __name__ == '__main__':
    main()
