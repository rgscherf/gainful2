import requests
import re
import dateutil.parser as d
from datetime import date, timedelta
from .jobcontainer import JobContainer
from bs4 import BeautifulSoup

def get_icims_jobs(region, org, soup):
    job_table = soup.find(class_="iCIMS_JobsTable").tbody
    rows = job_table.find_all("tr")
    for row in rows:
        job = JobContainer()
        cols = row.find_all("td")
        job.url_detail = cols[1].a["href"]
        if not job.is_unique():
            continue
        job.region = region
        job.organization = org
        job.title = cols[1].a.text.strip()
        date_posted_text = cols[3].find_all("span")[1].text.strip()
        job.date_posted = d.parse(date_posted_text).date()
        job = parse_detail_page(job)
        job.save()

def fail_re(retext, msg):
    print(retext)
    print()
    print(msg)
    raise NotImplementedError

def parse_detail_page(job):
    """ Grab mississauga info from detail page:
    division, salary type and amount, and closing date.
    """
    r = requests.get(job.url_detail)
    soup = BeautifulSoup(r.text, "html5lib")
    job_text = soup.find(class_="iCIMS_Expandable_Text").text
    job.salary_amount = salary(job_text)
    job.division = division(job_text)
    job.date_closing = closing(job_text)
    return job

def closing(text):
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

def division(text):
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
        result = result.group(2).strip()
    else:
        fail_re(text, "IMPLEMENT DIVISION PARSE")
    return result

def salary(text):
    search = re.compile(r"\$([0-9]*.[0-9]*)")
    result = search.search(text)
    if result:
        result = result.group()
        result = result[1:]
        if "," in result:
            result = "".join(filter(lambda x: x != ",", result))
        try:
            result = float(result)
        except ValueError:
            result = 0
    else:
        result = 0
    return result
