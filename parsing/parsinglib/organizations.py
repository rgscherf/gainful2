import json
import shutil
import os
import requests
import PyPDF2
import re
from itertools import takewhile, dropwhile
from datetime import date, timedelta
from bs4 import BeautifulSoup
from .jobcontainer import JobContainer
import dateutil.parser as d


def fail_re(retext, msg):
    print(retext)
    print()
    print(msg)
    raise NotImplementedError


def get_pdf(url):
    """ Retrieve PDF from a URL.
    :param url: string pointing to a pdf URL
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

def dump_soup(soup):
    ret = ""
    for child in soup.children:
        ret += child.text
    return ret



class Organization():
    def __init__(self, name):
        with open(os.path.join(os.path.abspath("."), "parsing/parsinglib/orgs.json")) as FILE:
            d = json.load(FILE)
            self.request_url = d[name]["request_url"]

    def parse(self, soup):
        raise NotImplementedError


class Mississauga(Organization):
    def __init__(self):
        Organization.__init__(self, "mississauga")

    def parse(self, soup):
        job_table = soup.find(class_="iCIMS_JobsTable").tbody
        rows = job_table.find_all("tr")
        for row in rows:
            job = JobContainer()
            cols = row.find_all("td")
            job.url_detail = cols[1].a["href"]
            if job.is_unique():
                pass
            else:
                print("Job already exists in DB: {}".format(job.url_detail))
            job.organization = "Mississauga"
            job.title = cols[1].a.text.strip()
            date_posted_text = cols[3].find_all("span")[1].text.strip()
            job.date_posted = d.parse(date_posted_text).date()
            self.parse_detail_page(job)
            job.save()

    def parse_detail_page(self, job):
        """ Grab mississauga info from detail page:
        division, salary type and amount, and closing date.
        """
        r = requests.get(job.url_detail)
        soup = BeautifulSoup(r.text, "html5lib")
        job_text = soup.find(class_="iCIMS_Expandable_Text").text
        job.salary_waged, job.salary_amount = self.salary(job_text)
        job.division = self.division(job_text)
        job.date_closing = self.closing(job_text)

    def closing(self, text):
        fallback = date.today() + timedelta(days=21)
        search = re.compile(r"Closing Date:(| )([\S|\s]*[0-9](, |th, )[0-9]{4})")
        result = search.search(text)
        if result:
            result = result.group(2)
            try:
                closing = d.parse(result).date()
            except ValueError:
                closing = fallback
        else:
            closing = fallback
        return closing

    def division(self, text):
        if "Division:" in text:
            search = re.compile(r"Division:(| )([\w\s]*)")
        elif "Unit:" in text:
            search = re.compile(r"Unit:(| )([\w\s]*)")
        elif "Department:" in text:
            search = re.compile(r"Department:(| )([\w\s]*)")
        else:
            return ""
        result = search.search(text)
        if result:
            result = result.group(2)
        else:
            fail_re(text, "IMPLEMENT DIVISION PARSE")
        return result

    def salary(self, text):
        waged = True if "Hourly Rate:" in text else False
        search = re.compile(r"\$([0-9]*.[0-9]*)")
        result = search.search(text)
        if result:
            result = result.group()
            result = result[1:]
            if "," in result:
                result = "".join(filter(lambda x: x != ",", result))
        else:
            fail_re("could not find salary or hourly rate")
        return waged, float(result)


class Toronto(Organization):
    def __init__(self):
        Organization.__init__(self, "toronto")

    def parse(self, soup):
        job_table = soup.find("table", "job_list_table")
        rows = job_table.find_all('tr')[1:]
        for row in rows:
            job = JobContainer()
            cols = row.find_all('td')
            job.url_detail = "https://www.brainhunter.com/frontoffice/{}".format(cols[1].a["href"])
            if job.is_unique():
                pass
            else:
                print("Job already exists in DB: {}".format(job.url_detail))
                continue
            self.parse_detail_page(job)

    def parse_detail_page(self, job):
        """ Grab City of Toronto job info from detail page:
        title, division, salary type and amount, posting date and closing date.
         """
        r = requests.get(job.url_detail)
        soup = BeautifulSoup(r.text, "html5lib")
        job.organization = "City of Toronto"
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
        job.salary_waged, job.salary_amount = self.salary(rowdict["Salary/Rate"])
        job.save()

    def salary(self, string):
        waged = True if "hour" in string.lower() else False
        s = "".join(dropwhile(lambda x: not x.isdigit(), string))
        s = "".join(takewhile(lambda x: not x.isspace(), s))
        if "," in s:
            s = "".join(filter(lambda a: a != ",", s))
        amount = float("".join(s))
        return waged, amount


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
        job_table = soup.find("tbody")
        rows = job_table.find_all('tr')
        rows = rows [1:]
        for row in rows:
            job = JobContainer()
            cols = row.find_all('td')
            # insert these fields before tags are stripped from columns!
            job.url_detail = "http://victoria.ca{}".format(cols[6].a["href"])
            if job.is_unique():
                pass
            else:
                print("Job already exists in DB: {}".format(job.url_detail))
                continue
            job.salary_waged, job.salary_amount = self.get_salary_from_pdf("http://victoria.ca/{}".format(cols[6].a["href"]))

            # information for these fields can be taken from stripped cols
            cols = [elem.text.strip() for elem in cols]
            job.title = cols[0]
            job.organization = "City of Victoria"
            job.division = cols[2]
            job.date_closing = d.parse(cols[4]).date()
            job.date_posted = date.today()
            job.save()
