from parsing.parsinglib import org_handler
from django.core.management.base import BaseCommand
from parsing.models import Job
from parsing.serializers import JobSerializer
from rest_framework.renderers import JSONRenderer
import datetime

orgs = org_handler.current_orgs
filename = "parsing/static/parsing/jobs.json"

class Command(BaseCommand):
    def handle(self, *args, **options):
        org_handler.find_jobs()
        print("Got new jobs.")
        print("Deleting expired jobs...")
        expired_jobs = Job.objects.filter(date_closing__lt=datetime.date.today())
        deletion_result = expired_jobs.delete()
        print("Deleted {} jobs.".format(deletion_result[0]))
        print("Writing jobs to file...")
        objs = Job.objects.all()
        serializer = map(lambda o: JobSerializer(o).data, objs)
        content = JSONRenderer().render(serializer)

        with (open(filename, "wb")) as FILE:
            FILE.write(content)
            print("Wrote jobs to {}".format(filename))



