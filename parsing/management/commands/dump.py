from django.core.management.base import BaseCommand
from parsing.models import Job
from parsing.serializers import JobSerializer
from rest_framework.renderers import JSONRenderer
import os

filename = os.path.abspath(".") + "/parsing/static/parsing/jobs.json"

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.write_jobs(filename)

    def write_jobs(self, file):
        objs = Job.objects.all().order_by("-date_posted")
        print("Found {} jobs in DB".format(len(objs)))
        print("Writing jobs to file...")
        serializer = []
        for o in objs:
            serializer.append(JobSerializer(o).data)
        content = JSONRenderer().render(serializer)
        with open(file, "wb") as FILE:
            FILE.write(content)
        if os.path.isfile(file):
            print("Wrote jobs.json to {}".format(file))
        else:
            print("Failed to write jobs.json to {}".format(file))


