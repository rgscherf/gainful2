from parsing.parsinglib import org_handler
from django.core.management.base import BaseCommand
from parsing.models import Job
import datetime
import os

orgs = org_handler.current_orgs
filename = os.path.abspath(".") + "/parsing/static/parsing/jobs.json"

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.get_jobs()
        self.delete_expired_jobs()

    def get_jobs(self):
        print("Getting new jobs.")
        org_handler.find_jobs()
        print("Got new jobs.")

    def delete_expired_jobs(self):
        print("Deleting expired jobs...")
        expired_jobs = Job.objects.filter(date_closing__lt=datetime.date.today())
        deletion_result = expired_jobs.delete()
        print("Deleted {} jobs.".format(deletion_result[0]))

