import requests
import datetime
import dateutil.parser as d
from bs4 import BeautifulSoup
from itertools import takewhile, dropwhile
from .jobcontainer import JobContainer

def parse_brainhunter_job_table(soup):
    ret = []
    job_table = soup.find("table", "job_list_table")
    rows = job_table.find_all('tr')[1:]
    for row in rows:
        job = JobContainer()
        cols = row.find_all('td')
        job.url_detail = "https://www.brainhunter.com/frontoffice/{}".format(cols[1].a["href"])
        if not job.is_unique():
            continue
        ret.append(job)
    return ret

def parse_brainhunter_detail_page(field_dict, job):
    """ parse brainhunter detail page.
    param field_dict: dictionary of job field names FOR THIS ORGANIZATION.
        checked fields: division, date_posted, date_closing, salary_amount
    param job: JobContainer object
    """
    r = requests.get(job.url_detail)
    soup = BeautifulSoup(r.text, "html5lib")
    job.title = soup.find("div", class_="tableheadertext_job_description").text.strip()
    rows = soup.find("table", class_="tablebackground_job_description").find_all("tr")
    rowdict = {}
    cols = field_dict.values()
    for row in rows:
        col = row.find(class_="job_header_text_bold").text.strip()
        if col in cols:
            rowdict[col] = row.find(class_="job_header_text").text.strip()
    job.division = rowdict[field_dict["division"]]
    job.date_posted = d.parse(rowdict[field_dict["date_posted"]]).date()
    job.date_closing = d.parse(rowdict[field_dict["date_closing"]]).date()
    try: 
        job.salary_amount = brainhunter_extract_salary(rowdict[field_dict["salary_amount"]])
    except KeyError:
        job.salary_amount = 0
    job.save()

def brainhunter_detail_page_exception(job, error):
    print("BRAINHUNTER DETAIL PARSE FAILED for key {} on job {}".format(error, job.url_detail))

def brainhunter_extract_salary(string):
    s = "".join(dropwhile(lambda x: not x.isdigit(), string))
    s = "".join(takewhile(lambda x: not x.isspace(), s))
    if "-" in s:
        s = s.split("-")[0]
    if "," in s:
        s = "".join(filter(lambda a: a != ",", s))
    if len(list(filter(lambda c: c.isdigit(), s))) == 0: # float() will fail if this is true, but just want to be explicit about it
        raise IndexError("Tried to extract salary from non-number: {}".format(s))
    try:
        amount = float("".join(s))
    except (ValueError, IndexError):
        print("BAINHUNTER PARSE ERROR ON VALUE: {}".format(amount))
        amount = 0
    return amount
