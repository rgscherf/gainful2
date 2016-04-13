# import shutil
# import PyPDF2
# import json
# import os
import requests
import re
import dateutil.parser as d
from datetime import date, timedelta
from bs4 import BeautifulSoup
from itertools import dropwhile
from .jobcontainer import JobContainer
from .org_urls import urls
from .utils_icims import get_icims_jobs
from .utils_brainhunter import parse_brainhunter_job_table, parse_brainhunter_detail_page, brainhunter_extract_salary


class Organization():
    def __init__(self, org_name):
        request_url = urls[org_name]
        r = requests.get(request_url)
        self.soup = BeautifulSoup(r.text, "html5lib")

    def parse(self, soup):
        raise NotImplementedError


class PeelRegion(Organization):
    def __init__(self):
        Organization.__init__(self, "peel_region")

    def parse(self):
        get_icims_jobs("GTA - Peel", "Peel Region", self.soup)


class Mississauga(Organization):
    def __init__(self):
        Organization.__init__(self, "mississauga")

    def parse(self):
        get_icims_jobs("GTA - Peel", "Mississauga", self.soup)


class Brampton(Organization):
    # brampton works, but does not capture closing dates for seasonal vacancies
    # (these dates are written inline on the page)
    def __init__(self):
        Organization.__init__(self, "brampton")

    def parse(self):
        get_icims_jobs("GTA - Peel", "Brampton", self.soup)


class YorkRegion(Organization):
    def __init__(self):
        Organization.__init__(self, "york_region")

    def make_url(self, cs):
        """ there's a bunch of junk in these job urls
        including an expiring token. Luckily, we can chop out the token
        and the server will insert one for us on request.
        (saving the chopped URL ensures we'll properly detect uniques in the DB)
        """
        tempurl = cs[1].a["href"]
        tempurl = tempurl.split("clid=")[1].split("&BRID=")[0]
        url = "http://clients.njoyn.com/cl2/xweb/Xweb.asp?clid={}".format(tempurl)
        return url

    def parse_detail_page(self, job):
        def stringops_removechar(char, string):
            if char in string:
                return "".join(filter(lambda a: a != char, string))
            else:
                return string
        req = requests.get(job.url_detail)
        soup = BeautifulSoup(req.text, "html5lib")
        info_table = soup.find("table").find_all("tr")
        # search header table for basic info
        for r in info_table:
            cells = r.find_all("td")
            field_name = cells[0].text
            try:
                val = cells[1].text.strip()
            except IndexError:
                continue
            if "Department" in field_name:
                if " Department" in val:
                    val = val.split(" Department")[0]
                job.division = val
            elif "Date Posted" in field_name:
                job.date_posted = d.parse(val)
            elif "Date Closing" in field_name:
                job.date_closing = d.parse(val)
        if not job.date_closing:
            job.date_closing = date.today() + timedelta(weeks=3)
        # now searching the body text for salary information
        # I think we only incur regex expense when we compile
        # so iteration is not too too bad.
        body = soup.find_all("p")
        ex = re.compile(r"\$[0-9]*(.|,)[0-9]*")
        for p in body:
            text = p.text
            result = ex.search(text)
            if result:
                result = result.group(0)[1:]
                result = stringops_removechar(",", result)
                job.salary_amount = float(result)
            else:
                pass

    def parse(self):
        t = self.soup.find(id="searchtable").find_all("tr")[1:]
        for r in t:
            job = JobContainer()
            cols = r.find_all("td")
            job.url_detail = self.make_url(cols)
            if not job.is_unique():
                continue
            job.region = "GTA - York"
            job.organization = "York Region"
            job.title = cols[1].text
            self.parse_detail_page(job)
            job.save()

class Toronto(Organization):
    def __init__(self):
        Organization.__init__(self, "toronto")

    def parse(self):
        detail_dict = { "division": "Division"
                      , "date_posted": "Posting Date"
                      , "date_closing": "Closing Date"
                      , "salary_amount": "Salary/Rate"
                      }
        for j in parse_brainhunter_job_table(self.soup):
            j.region = "GTA - Toronto"
            j.organization = "Toronto"
            parse_brainhunter_detail_page(detail_dict, j)

class Markham(Organization):
    def __init__(self):
        Organization.__init__(self, "markham")

    def parse(self):
        detail_dict = { "division": "Department"
                      , "date_posted": "Posting Date"
                      , "date_closing": "Expiry Date"
                      , "salary_amount": "Salary/Rate"
                      }
        for j in parse_brainhunter_job_table(self.soup):
            j.region = "GTA - York"
            j.organization = "Markham"
            parse_brainhunter_detail_page(detail_dict, j)

class Halton(Organization):
    def __init__(self):
        Organization.__init__(self, "halton")

    def parse(self):
        rows = self.soup.find(class_="List").find_all("tr")[2:]
        for r in rows:
            job = JobContainer()
            cols = r.find_all("td")
            job.url_detail = "http://webaps.halton.ca/about/jobs/" + cols[0].a["href"]
            if not job.is_unique():
                continue
            job.organization = "Halton Region"
            job.region = "GTA - Halton"
            job.title = cols[0].text.strip()
            job.division = cols[1].text.strip()
            self.parse_detail_page(job)
            job.save()

    def parse_detail_page(self, job):
        r = requests.get(job.url_detail)
        soup = BeautifulSoup(r.text, "html5lib")
        rows = soup.find_all("tr")
        for r in rows:
            cols = r.find_all("td")
            cols = list(dropwhile(lambda x: x.text.strip().lower() == "", cols))
            if len(cols) < 2:
                continue
            field = cols[0].text.strip().lower()
            val = cols[1].text.strip()
            if field == "salary range:":
                job.salary_amount = brainhunter_extract_salary(val)
            elif field == "posted:":
                job.date_posted = d.parse(val).date()
            elif "posting ex" in field:
                job.date_closing = d.parse(val).date()

class Burlington(Organization):
    def __init__(self):
        Organization.__init__(self, "burlington")

    def parse(self):
        rows = self.soup.find(class_="TPListTbl").find_all("tr")[1:]
        for r in rows:
            cols = r.find_all("td")
            job = JobContainer()
            job.url_detail = "http://careers2.hiredesk.net" + cols[0].a["href"]
            if not job.is_unique():
                continue
            job.title = cols[0].text.strip()
            job.region = "GTA - Halton"
            job.organization = "Burlington"
            job.date_posted = date.today()
            job.date_closing = d.parse(cols[4].text.strip()).date()
            self.parse_detail_page(job)
            job.save()

    def parse_detail_page(self, job):
        """ get job's department and salary
        """
        r = requests.get(job.url_detail)
        soup = BeautifulSoup(r.text, "html5lib")
        rows = soup.find(class_="FormContent").find_all("tr")
        for r in rows:
            cols = r.find_all("td")
            if len(cols) < 2:
                continue
            field = cols[0].text.strip().lower()
            val = cols[1].text.strip()
            if field == "department":
                job.division = val
            elif field == "salary range" or field == "hourly rate":
                job.salary_amount = brainhunter_extract_salary(val)
        if job.division == None:
            job.division = ""


# the main parse util calls find_jobs to kick off web scraping.
# make sure current_orgs is always up to date.

current_orgs = [ Burlington()
               , Halton()
               , Markham()
               , YorkRegion()
               , Brampton()
               , PeelRegion()
               , Mississauga()
               , Toronto()
               ]

def find_jobs():
    for o in current_orgs:
        o.parse()

