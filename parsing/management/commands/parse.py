from parsing.parsinglib import org_handler
from django.core.management.base import BaseCommand
from parsing.models import Job
from parsing.serializers import JobSerializer
from rest_framework.renderers import JSONRenderer

orgs = org_handler.current_orgs

class Command(BaseCommand):
    def handle(self, *args, **options):
        org_handler.find_jobs()
        print("Got new jobs.")
        print("Dumping jobs to file...")
        objs = Job.objects.all()
        serializer = []
        for o in objs:
            i = JobSerializer(o).data
            serializer.append(i)
        content = JSONRenderer().render(serializer)
        with (open("parsing/static/parsing/jobs.json", "wb")) as FILE:
            FILE.write(content)


