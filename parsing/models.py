from django.db import models

class Job(models.Model):
    id = models.AutoField(primary_key=True)
    organization = models.CharField(max_length=100)
    title = models.CharField(max_length=300)
    division = models.CharField(max_length=100)
    date_posted = models.DateField()
    date_closing = models.DateField()
    date_collected = models.DateField()
    url_detail = models.CharField(max_length=500)
    salary_waged = models.BooleanField()
    salary_amount = models.FloatField()
    region = models.CharField(max_length=100)

    def __str__(self):
        return "{} at {}".format(self.title, self.organization)
