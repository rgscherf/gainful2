from bs4 import BeautifulSoup
from itertools import chain
import requests
import organizations

organizations = [ organizations.Toronto()
         , organizations.Hamilton()
         , organizations.Mississauga()
         , organizations.CRD()
         # , organizations.OPS()
         , organizations.BCPS()
         , organizations.CivicInfo()
         , organizations.CivicInfo_North_Central()
         , organizations.CivicInfo_Lower_Mainland()
         , organizations.AMCTO()
         ]
         
def parse(org):
    r = requests.get(org.request_url)
    rtext = r.text
    soup = BeautifulSoup(rtext, "lxml")
    data = org.make_data(soup)
    return data


def build_parse_list():
    source = []
    for o in organizations:
        source.append(parse(o))
        print "Parsed {}".format(o.name)
    flattened_list = list(chain.from_iterable(source))

    return flattened_list


# run update
# crawl each organization's site
# for each job:
# if there's no entry for job, save it to DB!
