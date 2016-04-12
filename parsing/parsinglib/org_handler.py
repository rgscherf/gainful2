# import shutil
# import PyPDF2
# import json
# import os
import requests
import re
import dateutil.parser as d
from datetime import date, timedelta
from bs4 import BeautifulSoup
from .jobcontainer import JobContainer
from .org_urls import urls
from .utils_icims import get_icims_jobs
from .utils_brainhunter import parse_brainhunter_job_table, parse_brainhunter_detail_page


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



# the main parse util calls find_jobs to kick off web scraping.
# make sure current_orgs is always up to date.

current_orgs = [ Markham()
               , YorkRegion()
               , Brampton()
               , PeelRegion()
               , Mississauga()
               , Toronto()
               ]

def find_jobs():
    for o in current_orgs:
        o.parse()

# def get_pdf(url):
#     """ Retrieve PDF from a URL.
#     :param url: string pointing to a pdf URL
#     :rtype string of PDF filename
#     """
#     filename = 'out.pdf'
#     r = requests.get(url, stream=True)
#     if r.status_code == 200:
#         with open(filename, 'wb') as OUTFILE:
#             shutil.copyfileobj(r.raw, OUTFILE)
#         return filename
#     else:
#         raise KeyError("Could not retrieve job description PDF.")
#
#
# def pdf_to_string(filename):
#     """Return the text of a PDF.
#     :param filename: string with root (no file extension) of filename
#     :rtype string of text in PDF
#     """
#     pdf = open(filename, 'rb')
#     pdfr = PyPDF2.PdfFileReader(pdf)
#     string = ""
#     for i in range(pdfr.getNumPages()):
#         page = pdfr.getPage(i)
#         string += page.extractText()
#     pdf.close()
#     os.remove(filename)
#     return string

# class Victoria(Organization):
#     def __init__(self):
#         Organization.__init__(self, "victoria")
#
#     def get_salary_from_pdf(self, url):
#         """ Pull PDF from a URL and search it for salary information.
#         :param url: URL to pull PDF from
#         :rtype tuple of (is_job_waged, pay_amount [where 0 indicates no posted salary])
#         """
#         f = get_pdf(url)
#         text = pdf_to_string(f)
#         try:
#             # PDF has no structure. Best bet to search for salary is to look for a $! :(
#             #... take digits until we find a space
#             #... and then cast that flattened list of digits into a float
#             text = text.split("$")[1]
#             salary_text = list(takewhile(lambda x: x != " ", text))
#             salary_text = filter(lambda x: x != "\n", salary_text)
#             salary_text = "".join(salary_text)
#             r_salary = float(salary_text)
#         except IndexError:
#             r_salary = 0
#         return r_salary
#
#     def parse(self, soup):
#         job_table = soup.find("tbody")
#         rows = job_table.find_all('tr')
#         rows = rows [1:]
#         for row in rows:
#             job = JobContainer()
#             cols = row.find_all('td')
#             # insert these fields before tags are stripped from columns!
#             job.url_detail = cols[0].a["href"]
#             print(job.url_detail)
#             if not job.is_unique():
#                 continue
#             job.salary_amount = self.get_salary_from_pdf(job.url_detail)
#
#             # information for these fields can be taken from stripped cols
#             cols = [elem.text.strip() for elem in cols]
#             job.title = cols[0]
#             job.region = "Vancouver Island"
#             job.organization = "City of Victoria"
#             job.division = cols[2]
#             job.date_closing = d.parse(cols[4]).date()
#             job.date_posted = date.today()
#             job.save()