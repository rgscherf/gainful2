################################################################################
# OUTPUT FORMAT:
# Job with fields: org[anization], [job] title, div[ision], [posting] date, [posting] url
# REDIS KEY IS "ORG:TITLE:URL"
################################################################################


def log(t):
    t = t.prettify().encode('utf-8')
    with open("log.html", "wb") as FILE:
        FILE.write(t)

def parse_date(date_string):
    if date_string == "":
        date = datetime.date.today()
    else:
        date = dp.parse(date_string)
    if date.day < 10:
        res = str(date.year) + "/" + str(date.month) + "/0" + str(date.day)
    else:
        res = str(date.year) + "/" + str(date.month) + "/" + str(date.day)
    return res

def parse_date_object(date):
    if date.day < 10:
        res = str(date.year) + "/" + str(date.month) + "/0" + str(date.day)
    else:
        res = str(date.year) + "/" + str(date.month) + "/" + str(date.day)
    return res


class Toronto(Organization):
    def __init__(self):
        Organization.__init__(self, "toronto")

    def parse(self, input_data):
        job_table = input_data.find(self.soup_find_list[0], self.soup_find_list[1])
        rows = job_table.find_all('tr')

        output_data = []
        first_row = True

        for row in rows:
            cols = row.find_all('td')
            cols = [elem.text.strip() for elem in cols]
            if first_row:
                cols.append("Job URL")
                first_row = False
            else:
                url = row.find('a')
                cols.append("https://www.brainhunter.com/frontoffice/" + url['href'].encode('ascii'))
            output_data.append([elem for elem in cols if elem])

        del output_data[0]
        # output_data.insert(0, ["Posting Date", "Job Title", "Division", "Job Type", "Job Location", "Job URL"])

        tags = ["municipal", "ontario"]
        processed_output = []
        for elem in output_data:
            key = "{}:{}:{}".format(self.name, elem[1], elem[5])
            job = Job(self.name, elem[1], elem[2], parse_date(elem[0]), elem[5], key, tags)
            processed_output.append(job)
        return processed_output


class Hamilton(Organization):
    def __init__(self):
        Organization.__init__(self, "hamilton")

    def parse(self, input_data):
        output_data = []
        job_table = input_data.find(self.soup_find_list[0], self.soup_find_list[1])
        rows = job_table.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            cols = [elem.text.encode('utf-8').strip() for elem in cols]
            cols.append('https://hr.hamilton.ca/psp/hr9eapps/EMPLOYEE/HRMS/c/HRS_HRAM.HRS_CE.GBL')
            output_data.append([elem for elem in cols if elem])

        # output_data.insert(0, ["Posting Date", "Job Title", "Job ID", "Department", "Job URL"])

        tags = ["municipal", "ontario"]
        processed_output = []
        for elem in output_data:
            key = "{}:{}:{}".format(self.name, elem[1], elem[4])
            job = Job(self.name, elem[1], elem[3], parse_date(elem[0]), elem[4], key, tags)
            processed_output.append(job)
        return processed_output


class Mississauga(Organization):
    def __init__(self):
        Organization.__init__(self, "mississauga")

    def parse(self, input_data):
        output_data = []
        job_table = input_data.find(self.soup_find_list[0], self.soup_find_list[1])
        rows = job_table.find_all('tr')

        first_row = True
        for row in rows:
            if first_row:
                first_row = not first_row
                continue
            date = row.find('td', 'iCIMS_JobsTableField_4').find_all('span')
            date = date[1].text.encode('utf-8').strip()
            title = row.find('a').text.encode('utf-8').strip()
            title = " ".join([word.capitalize() for word in title.split()])
            url = row.find('a')['href'].encode('utf-8')

            tags = ["municipal", "ontario"]
            key = "{}:{}:{}".format(self.name, title, url)
            job = Job(self.name, title, "City of Mississauga", parse_date(date), url, key, tags)
            output_data.append(job)
        return output_data

    def parse(self, input_data):
        output_data = []
        job_table = input_data.find(self.soup_find_list[0], self.soup_find_list[1])
        rows = job_table.find_all('tr')
        rows = rows[1:]

        for row in rows:
            cols = row.find_all('td')
            cols = [elem.text.strip() for elem in cols]
            urls = row.find_all('a')
            url = ('http://www.victoria.ca' + urls[1]['href']).encode('ascii')
            cols.append(url)
            output_data.append([elem for elem in cols if elem])

        # output_data.insert(0, ["Job Title", "Job ID", "Department", "Status", "Closing Date", "Apply", "Details", "Job URL"])

        processed_output = []
        tags = ["municipal", "bc"]
        for elem in output_data:
            key = "{}:{}:{}".format(self.name, elem[1], elem[7])
            job = Job(self.name, elem[0], elem[2], parse_date(""), elem[7], key, tags)
            processed_output.append(job)
        return processed_output


class CRD(Organization):
    def __init__(self):
        Organization.__init__(self, "crd")

    def parse(self, input_data):
        output_data = []
        job_table = input_data.find(self.soup_find_list[0], self.soup_find_list[1])
        job_table = job_table.find('table')
        rows = job_table.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            cols = [elem.text.strip() for elem in cols]
            url = row.find('a')
            if url:
                cols.append("http://www.crd.bc.ca" + url['href'].encode('utf-8'))
            output_data.append([elem for elem in cols if elem])

        del output_data[0]
        for elem in output_data:
            del elem[2]
        # output_data.insert(0, ["Job Title", "Closing Date", "Job URL"])

        processed_output = []
        tags = ["municipal", "bc"]
        for elem in output_data:
            key = "{}:{}:{}".format(self.name, elem[0], elem[2])
            job = Job(self.name, elem[0], "Capital Regional District", parse_date(""), elem[2], key, tags)
            processed_output.append(job)
        return processed_output


class OPS(Organization):
    def __init__(self):
        Organization.__init__(self, "ops")

    def parse(self, input_data):
        job_table = input_data.find(self.soup_find_list[0], self.soup_find_list[1])
        job_table = job_table.parent.table

        rows = job_table.find_all('a')

        output_data = []

        for row in rows:
            finished_row = []
            title = row.text.encode('utf-8').strip()
            finished_row.append(title)
            finished_row.append("https://www.gojobs.gov.on.ca/" + row['href'].encode('utf-8'))

            cols = row.parent.table
            cols = cols.find_all('span')

            odd = False
            for col in cols:
                if not odd:
                    odd = not odd
                    continue
                odd = not odd
                cleaned_string = col.text.encode('utf-8').strip()
                finished_row.append(cleaned_string)
            output_data.append(finished_row)

        # output_data.insert(0, ["Job Title", "Job URL", "Ministry", "Salary Range", "Location", "Closing Date"])

        tags = ["provincial", "ontario"]

        processed_output = []
        for elem in output_data:
            title = " ".join([word.capitalize() for word in elem[0].split()])
            key = "{}:{}:{}".format(self.name, title, elem[1])
            job = Job(self.name, title, elem[2], parse_date(""), elem[1], key, tags)
            processed_output.append(job)
        return processed_output

    def make_data_open_targeted(self, url):
        r = requests.get(url)
        rtext = r.text
        soup = BeautifulSoup(rtext, "lxml")

        title = soup.find("font", style="font-family:Verdana; font-size:140%; font-weight:bold; color:#000000;").text.encode('utf-8').strip()
        title = " ".join([word.capitalize() for word in title.split()])

        job_table = soup.find("table", id="JobAdTable_1")
        rows = job_table.find_all("tr")

        div = rows[1].find_all("td")
        div = div[2].text.encode('utf-8').strip()

        date = parse_date("")
        url = url
        key = "{}:{}:{}".format(self.name, title, url)
        tags = ["provincial", "ontario", "open_targeted"]

        job = Job(self.name, title, div, date, url, key, tags)
        return job


class BCPS(Organization):
    def __init__(self):
        Organization.__init__(self, "bcps")

    def unpad_title(self, string):
        if "-" in string:
            r = self.dropwhile(lambda x: x != " ", string)
            r = self.dropwhile(lambda x: x != "-", r)
            r = self.dropwhile(lambda x: x != " ", r)
            r = r[1:]
        else:
            r = string
        return r

    def parse(self, input_data):

        job_table = input_data.find(self.soup_find_list[0], self.soup_find_list[1])
        rows = job_table.find_all('tr', 'tdcolor')

        output_data = []
        tags = ["provincial", "bc"]
        for row in rows:
            url = "https://search.employment.gov.bc.ca" + row.find('a')['href']
            cols = row.find_all('td')

            div = cols[0].text.encode('utf-8').strip()
            padded_title = cols[2].text.encode('utf-8').strip()
            title = padded_title.split(" - ")[1] if " - " in padded_title else padded_title
            date = parse_date(cols[5].text.encode('utf-8').strip())

            key = "{}:{}:{}".format(self.name, title, url)
            job = Job(self.name, title, div, date, url, key, tags)
            output_data.append(job)

        return output_data


class CivicInfo(Organization):
    def __init__(self):
        Organization.__init__(self, "civicinfo")

    def unpad_date(self, string):
        r = string
        r = self.dropwhile(lambda x: x != "(", string)
        r = r[1:]
        r = self.takewhile(lambda x: x != ")", r)
        return r

    def pack_date(self, string):
        s = self.dropwhile(lambda x: x != ":", string)
        s = s[2:]
        s = s.split(", ")
        s = s[0:2]
        r = " ".join(s)
        r = parse_date(r)
        return r

    def parse(self, input_data):

        job_table = input_data.find(self.soup_find_list[0], self.soup_find_list[1])
        log(job_table)
        rows = job_table.find_all('li')

        output_data = []
        for row in rows:
            url = "http://www.civicinfo.bc.ca/" + row.find('a')['href']
            org_suffix = row.a.b.i.text.encode('utf-8').strip()
            row.i.decompose()
            title = row.a.b.text.encode('utf-8').strip()[:-2]

            date_text = row.find('br').nextSibling.strip()
            date_unformatted = self.unpad_date(date_text)
            date = self.pack_date(date_unformatted)

            # org = self.name + org_suffix
            org = org_suffix # "CivicInfo: City of XXXXXX" started to get ugly

            tags = ["municipal", "bc"]
            key = "{}:{}:{}".format(org, title, url)
            job = Job(org, title, org_suffix, date, url, key, tags)
            output_data.append(job)

        return output_data

class CivicInfo_North_Central(CivicInfo):
    def __init__(self):
        super(CivicInfo_North_Central, self).__init__()
        Organization.__init__(self, "civicinfo_north_central")

class CivicInfo_Lower_Mainland(CivicInfo):
    def __init__(self):
        super(CivicInfo_Lower_Mainland, self).__init__()
        Organization.__init__(self, "civicinfo_lower_mainland")

class AMCTO(Organization):
    def __init__(self):
        Organization.__init__(self, "amcto")

    def clean_url_text(self, string):
        string = self.dropwhile(lambda x: x != "C", string)
        return "http://www.amcto.com/imis15/content/" + string

    def extract_org_title(self, string):
        split = string.split(" - ")
        div = split[0]
        title = split[1]
        return div, title

    def parse(self, input_data):
        job_table = input_data.find(self.soup_find_list[0], self.soup_find_list[1])
        rows = job_table.find_all("table")

        output_data = []
        for row in rows:
            text = row.a
            url = text['href'].encode('utf-8')
            url = self.clean_url_text(url)
            text = text.text.encode('utf-8')
            div, title = self.extract_org_title(text)
            date = parse_date(row.span.span.span.text.encode('utf-8'))
            # name = self.name + div
            name = div # "AMCTO: City of XXXXXXX" started to get ugly

            tags = ["municipal", "ontario"]
            key = "{}:{}:{}".format(self.name, title, url)
            job = Job(name, title, div, date, url, key, tags)
            output_data.append(job)

        return output_data
