from ..models import Job

class JobContainer():
    def __init__(self):
        self.organization = None
        self.title = None
        self.division = None
        self.date_posted = None
        self.date_closing = None
        self.url_detail = None
        self.url_apply = None
        self.salary_waged = None
        self.salary_amount = None

    def get_fields(self):
        return [self.organization
                , self.title
                , self.division
                , self.date_posted
                , self.date_closing
                , self.url_detail
                , self.url_apply
                , self.salary_waged
                , self.salary_amount
                ]

    def __str__(self):
        return "{} at {}".format(self.title, self.organization)

    def validate(self):
        return False if None in self.get_fields() else True

    def is_unique(self):
        if not self.url_detail:
            raise KeyError("Queried record uniqueness before detail URL set: {}".format(self))
        else:
            return True if len(Job.objects.filter(url_detail=self.url_detail)) == 0 else False

    def save(self):
        if not self.validate():
            raise KeyError("Fields missing for {}".format(self))
        else:
            j = Job(organization=self.organization
                    , title=self.title
                    , division=self.division
                    , date_posted=self.date_posted
                    , date_closing=self.date_closing
                    , url_detail=self.url_detail
                    , url_apply=self.url_apply
                    , salary_waged=self.salary_waged
                    , salary_amount=self.salary_amount
                    )
            j.save()
