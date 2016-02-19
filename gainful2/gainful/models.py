from django.db import models

class Job():#models.Model):
    # id = models.AutoField(primary_key=True)
    # organization = models.CharField(max_length=100)
    # title = models.CharField(max_length=300)
    # division = models.CharField(max_length=100)
    # date_posted = models.DateField()
    # date_closing = models.DateField()
    # url = models.CharField(max_length=500)
    # salary = models.IntegerField()

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

    def fields(self):
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
        return False if None in self.fields() else True

    def save(self):
        if self.validate():
            print("OK! Found {}".format(self))
        else:
            raise KeyError("Fields missing for {}".format(self))
