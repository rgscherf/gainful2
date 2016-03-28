# import shutil
# import PyPDF2
# import json
# import os
import requests
import re
from datetime import date, timedelta
from itertools import takewhile, dropwhile
from bs4 import BeautifulSoup
from .jobcontainer import JobContainer
from .org_urls import urls
from .utils_icims import get_icims_jobs
import dateutil.parser as d


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
    # brampton works, but does not capture closing dates for season vacancies
    # (these dates are written inline on the page)
    def __init__(self):
        Organization.__init__(self, "brampton")

    def parse(self):
        get_icims_jobs("GTA - Peel", "Brampton", self.soup)


class YorkRegion(Organization):
    def __init__(self):
        Organization.__init__(self, "york_region")

    def make_url(cs):
        """ there's a bunch of junk in these job urls
        including an expiring token. Luckily, we can chop out the token
        and the server will insert one for us on request.
        (saving the chopped URL ensures we'll properly detect uniques in the DB)
        """
        tempurl = cs[1].a["href"]
        tempurl = tempurl.split("clid=")[1].split("&BRID=")[0]
        url = "http://clients.njoyn.com/cl2/xweb/Xweb.asp?clid={}".format(tempurl)
        return url

    def parse_detail_page(job):
        req = requests.get(job.url_detail)
        soup = BeautifulSoup(req.text, "html5lib")
        TODO: parse deail page!!

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
            job.date_closing = d.parse(cols[2].text).date()
            self.parse_detail_page(job)

class Toronto(Organization):
    def __init__(self):
        Organization.__init__(self, "toronto")

    def parse(self):
        job_table = self.soup.find("table", "job_list_table")
        rows = job_table.find_all('tr')[1:]
        for row in rows:
            job = JobContainer()
            cols = row.find_all('td')
            job.url_detail = "https://www.brainhunter.com/frontoffice/{}".format(cols[1].a["href"])
            if not job.is_unique():
                continue
            self.parse_detail_page(job)

    def parse_detail_page(self, job):
        """ Grab City of Toronto job info from detail page:
        title, division, salary type and amount, posting date and closing date.
         """
        r = requests.get(job.url_detail)
        soup = BeautifulSoup(r.text, "html5lib")
        job.region = "GTA - Toronto"
        job.organization = "Toronto"
        job.title = soup.find("div", class_="tableheadertext_job_description").text.strip()
        rows = soup.find("table", class_="tablebackground_job_description").find_all("tr")

        cols = ["Division", "Salary/Rate", "Posting Date", "Closing Date"]
        rowdict = {}
        for row in rows:
            col = row.find(class_="job_header_text_bold").text.strip()
            if col in cols:
                rowdict[col] = row.find(class_="job_header_text").text.strip()
        job.division = rowdict["Division"]
        job.date_posted = d.parse(rowdict["Posting Date"]).date()
        job.date_closing = d.parse(rowdict["Closing Date"]).date()
        try: # it's rare, but sometime Toronto doesn't post salary
            job.salary_amount = self.salary(rowdict["Salary/Rate"])
        except KeyError:
            job.salary_amount = 0
        job.save()

    def salary(self, string):
        s = "".join(dropwhile(lambda x: not x.isdigit(), string))
        s = "".join(takewhile(lambda x: not x.isspace(), s))
        if "," in s:
            s = "".join(filter(lambda a: a != ",", s))
        amount = float("".join(s))
        return amount



# the main parse util calls find_jobs to kick off web scraping.
# make sure current_orgs is always up to date.

current_orgs = [ YorkRegion()
               # , Brampton()
               # , PeelRegion()
               # , Mississauga()
               # , Toronto()
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