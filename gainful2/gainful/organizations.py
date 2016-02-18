import json
import shutil
import os
from itertools import takewhile
from datetime import date

import requests
import PyPDF2
import dateutil.parser as d
from bs4 import BeautifulSoup


def get_pdf(url):
    """ Retrieve PDF from a URL.
    :param url: string pointing to a pdf URL
    :param filename string with root (no file extension) of filename
    :rtype string of PDF filename
    """
    filename = 'out.pdf'
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(filename, 'wb') as OUTFILE:
            shutil.copyfileobj(r.raw, OUTFILE)
        return filename
    else:
        raise KeyError("Could not retrieve job description PDF.")

def pdf_to_string(filename):
    """Return the text of a PDF.
    :param filename: string with root (no file extension) of filename
    :rtype string of text in PDF
    """
    pdf = open(filename, 'rb')
    pdfr = PyPDF2.PdfFileReader(pdf)
    string = ""
    for i in range(pdfr.getNumPages()):
        page = pdfr.getPage(i)
        string += page.extractText()
    pdf.close()
    os.remove(filename)
    return string


class Organization():
    def __init__(self, name):
        with open("orgs.json") as FILE:
            d = json.load(FILE)
            self.request_url = d[name]["request_url"]
            self.soup_find_list = d[name]["soup_find_list"]
            self.csv_name = d[name]["csv_name"]
            self.name = d[name]["name"]


class Job():
    """ this will have to be changed from a job object to a DB entry """
    def __init__(self):
        self.org = None
        self.title = None
        self.division = None
        self.date_open = None
        self.date_close = None
        self.url_detail = None
        self.url_apply = None
        self.salary_amount = None
        self.salary_waged = None

    def validate(self):
        if None in [self.org, self.title, self.division, self.date_open, self.date_close, self.url_detail, self.url_apply, self.salary_amount, self.salary_waged]:
            raise KeyError("Not all job fields were defined for {}".format(self))

    def __str__(self):
        return "{} at {}".format(self.title, self.org)

    def save(self):
        """ Validate fields for Job. If valid, save to DB.
        TODO: at what point do we check whether this Job might be a duplicate DB entry?
        By this point, we've already downloaded and parsed a PDF. Extremely expensive.
        """
        try:
            self.validate()
            print(self)
            # db.save()
        except KeyError as e:
            print("KEYERROR", e)


class Victoria(Organization):
    def __init__(self):
        Organization.__init__(self, "victoria")

    def get_salary_from_pdf(self, url):
        """ Pull PDF from a URL and search it for salary information.
        :param url: URL to pull PDF from
        :rtype tuple of (is_job_waged, pay_amount [where 0 indicates no posted salary])
        """
        f = get_pdf(url)
        text = pdf_to_string(f)
        r_wage = True if "per hour" in text else False
        try:
            # PDF has no structure. Best bet to search for salary is to look for a $! :(
            #... take digits until we find a space
            #... and then cast that flattened list of digits into a float
            text = text.split("$")[1]
            salary_text = list(takewhile(lambda x: x != " ", text))
            salary_text = filter(lambda x: x != "\n", salary_text)
            salary_text = "".join(salary_text)
            r_salary = float(salary_text)
        except IndexError:
            r_salary = 0
        return (r_wage, r_salary)

    def parse(self, soup):
        output = []
        job_table = soup.find("tbody")
        rows = job_table.find_all('tr')
        rows = rows [1:]
        for row in rows:
            job = Job()
            cols = row.find_all('td')
            # insert these fields before tags are stripped from columns!
            job.url_detail = "http://victoria.ca/{}".format(cols[6].a["href"])
            job.url_apply = "http://www.victoria.ca/EN/main/departments/hr/{}".format(cols[5].a["href"])
            job.salary_waged, job.salary_amount = self.get_salary_from_pdf("http://victoria.ca/{}".format(cols[6].a["href"]))

            # information for these fields can be taken from stripped cols
            cols = [elem.text.strip() for elem in cols]
            job.title = cols[0]
            job.org = "City of Victoria"
            job.division = cols[2]
            job.date_close = d.parse(cols[4]).date()
            job.date_open = date.today()
            job.save()
