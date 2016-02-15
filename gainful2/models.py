from django.db import models

class Job(models.Model):
    id = models.AutoField(primary_key=True)
    organization = models.CharField(max_length=100)
    title = models.CharField(max_length=300)
    division = models.CharField(max_length=100)
    date_posted = models.DateField()
    date_closing = models.DateField()
    url = models.CharField(max_length=500)
    salary = models.IntegerField()
    location = models.CharField(max_length=100)
