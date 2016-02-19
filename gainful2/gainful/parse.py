from bs4 import BeautifulSoup
import requests
import organizations

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

def parse(o):
    r = requests.get(o.request_url)
    soup = BeautifulSoup(r.text, "html5lib")
    return o.parse(soup)

def main():
    for o in orgs:
        parse(o)

if __name__ == '__main__':
    # for org in organizations:
    #     parse(org)
    main()
