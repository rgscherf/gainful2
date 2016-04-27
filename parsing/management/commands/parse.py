from parsing.parsinglib import org_handler
from django.core.management.base import BaseCommand
from parsing.models import Job
from parsing.serializers import JobSerializer
from rest_framework.renderers import JSONRenderer
import datetime
import os

orgs = org_handler.current_orgs
filename = os.path.abspath(".") + "/parsing/static/parsing/jobs.json"

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.get_jobs()
        self.delete_expired_jobs()
        self.write_jobs()

    def get_jobs(self):
        print("Getting new jobs.")
        org_handler.find_jobs()
        print("Got new jobs.")

    def delete_expired_jobs(self):
        print("Deleting expired jobs...")
        expired_jobs = Job.objects.filter(date_closing__lt=datetime.date.today())
        deletion_result = expired_jobs.delete()
        print("Deleted {} jobs.".format(deletion_result[0]))

    def write_jobs(self):
        print("Writing jobs to file...")
        objs = Job.objects.all()
        today = Job.objects.all().filter(date_posted=datetime.date.today())
        print("jobs for today:")
        for t in today:
            print(t)
        serializer = map(lambda o: JobSerializer(o).data, objs)
        content = JSONRenderer().render(serializer)

        if os.path.isfile(filename):
            print("jobs.json exists; deleting.")
            os.remove(filename)
        with open(filename, "wb") as FILE:
            FILE.write(content)
            print("Wrote {} bytes to {}".format(len(content), filename))



