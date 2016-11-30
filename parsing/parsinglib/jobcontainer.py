from ..models import Job
import datetime


class JobContainer():

    def __init__(self):
        self.organization = None
        self.title = None
        self.division = None
        self.date_posted = None
        self.date_closing = None
        self.date_collected = None
        self.url_detail = None
        self.salary_waged = None
        self.salary_amount = None
        self.region = None

    def is_unique(self):
        """ Checks whether job (denoted by URL) already exists in DB.
        Remember to use this function before doing any intense parsing operations.
        """
        if not self.url_detail:
            raise KeyError(
                "Queried record uniqueness before detail URL set: {}".format(self))
        else:
            if len(Job.objects.filter(url_detail=self.url_detail)) == 0:
                return True
            else:
                # print("Job already exists in DB: {}".format(self.url_detail))
                return False

    def cleanup(self):
        self.title = self.title.title() if self.title.isupper() else self.title
        self.salary_amount = 0 if self.salary_amount == None else self.salary_amount
        # totally arbitray amount
        self.salary_waged = True if self.salary_amount < 5000 else False
        self.date_collected = datetime.date.today()

    def validate(self):
        field_dict = self.__dict__
        attributes = {
            k: v for k, v in field_dict.items() if not k.startswith("_")}
        for k, v in attributes.items():
            if v == None:
                raise KeyError(
                    "Job {} was missing {}".format(self.url_detail, k))

    def save(self):
        """ Save job to DB, after final checks.
        """
        if not self.is_unique():  # failsafe in case we forgot to check this earlier.
            print(
                "{} tried to save a job hat is not unique!".format(self.organization))
            return
        self.cleanup()
        try:
            self.validate()
        except KeyError as err:
            print("|| EXCEPTION")
            print("|| ", err)
            return

        print("Saved job to DB: {}".format(self))
        j = Job(organization=self.organization, title=self.title, division=self.division, date_posted=self.date_posted, date_closing=self.date_closing, url_detail=self.url_detail, salary_waged=self.salary_waged, salary_amount=self.salary_amount, region=self.region, date_collected=self.date_collected
                )
        j.save()

    def __str__(self):
        return "{} at {}".format(self.title, self.organization)
