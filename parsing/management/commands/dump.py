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
        objs = Job.objects.all()
        print("Found {} jobs in DB".format(len(objs)))
        print("Writing jobs to file...")
        # today = Job.objects.all().filter(date_posted=datetime.date.today())
        # print("jobs for today:")
        # for t in today:
        #     print(t)
        serializer = []
        for o in objs:
            serializer.append(JobSerializer(o).data)
        # serializer = map(lambda o: JobSerializer(o).data, objs)
        content = JSONRenderer().render(serializer)
        # if os.path.isfile(file):
        #     print("jobs.json exists; deleting.")
        #     os.remove(file)
        with open(file, "wb") as FILE:
            FILE.write(content)
            print("Wrote {} bytes to {}".format(len(content), file))


