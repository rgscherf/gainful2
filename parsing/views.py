from django.shortcuts import render
from parsing.models import Job
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from parsing.serializers import JobSerializer


class JobViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows jobs to be viewed or edited.
    """
    queryset = Job.objects.all().order_by('url_detail')
    serializer_class = JobSerializer

def index(request):
    jobs = get_jobs()
    print(type(jobs))
    return render(request, 'parsing/index.html', {'jobs_json': jobs})

def get_jobs():
    objs = Job.objects.all().order_by("-date_posted")
    serializer = []
    for o in objs:
        serializer.append(JobSerializer(o).data)
    content = JSONRenderer().render(serializer)
    return content


# filename = os.path.abspath(".") + "/parsing/static/parsing/jobs.json"

# class Command(BaseCommand):
#     def handle(self, *args, **kwargs):
#         self.write_jobs(filename)

#     def write_jobs(self, file):
#         objs = Job.objects.all().order_by("-date_posted")
#         print("Found {} jobs in DB".format(len(objs)))
#         print("Writing jobs to file...")
#         serializer = []
#         for o in objs:
#             serializer.append(JobSerializer(o).data)
#         content = JSONRenderer().render(serializer)
#         with open(file, "wb") as FILE:
#             FILE.write(content)
#         if os.path.isfile(file):
#             print("Wrote jobs.json to {}".format(file))
#         else:
#             print("Failed to write jobs.json to {}".format(file))


