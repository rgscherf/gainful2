from bs4 import BeautifulSoup
import requests
import organizations

# orgs = [
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
#         ]

def parse(o):
    r = requests.get(o.request_url)
    soup = BeautifulSoup(r.text, "html5lib")
    return o.parse(soup)

# # do I need this anymore??
# def build_parse_list():
#     source = []
#     for o in organizations:
#         source.append(parse(o))
#         print "Parsed {}".format(o.name)
#     flattened_list = list(chain.from_iterable(source))
#     return flattened_list


# run update
# crawl each organization's site
# for each job:
# if there's no entry for job, save it to DB!

if __name__ == '__main__':
    # for org in organizations:
    #     parse(org)
    parse( organizations.Victoria() )
