from ..models import Job

class JobContainer():
    def __init__(self):
        self.organization = None
        self.title = None
        self.division = None
        self.date_posted = None
        self.date_closing = None
        self.url_detail = None
        self.salary_waged = None
        self.salary_amount = None
        self.region = None

    def is_unique(self):
        """ Checks whether job (denoted by URL) already exists in DB.
        Remember to use this function before doing any intense parsing operations.
        """
        if not self.url_detail:
            raise KeyError("Queried record uniqueness before detail URL set: {}".format(self))
        else:
            return True if len(Job.objects.filter(url_detail=self.url_detail)) == 0 else False

    def cleanup(self):
        self.title = self.title.title() if self.title.isupper() else self.title
        self.salary_waged = True if self.salary_amount < 5000 else False # totally arbitray amount

    def get_fields(self):
        return [self.organization
                , self.title
                , self.division
                , self.date_posted
                , self.date_closing
                , self.url_detail
                , self.salary_waged
                , self.salary_amount
                , self.region
                ]

    def validate(self):
        return False if None in self.get_fields() else True

    def save(self):
        """ Save job to DB, after final checks.
        """
        if not self.is_unique(): # failsafe in case we forgot to check this earlier.
            print("{} tried to save a job that is not unique!".format(self.organization))
            return
        self.cleanup()
        if not self.validate():
            raise KeyError("Fields missing for {}".format(self))
        else:
            j = Job(organization=self.organization
                    , title=self.title
                    , division=self.division
                    , date_posted=self.date_posted
                    , date_closing=self.date_closing
                    , url_detail=self.url_detail
                    , salary_waged=self.salary_waged
                    , salary_amount=self.salary_amount
                    , region=self.region
                    )
            j.save()

    def __str__(self):
        return "{} at {}".format(self.title, self.organization)
