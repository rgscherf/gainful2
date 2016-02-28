from django.shortcuts import render

# Create your views here.
from parsing.models import Job
from rest_framework import viewsets
from parsing.serializers import JobSerializer


class JobViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows jobs to be viewed or edited.
    """
    queryset = Job.objects.all().order_by('url_detail')
    serializer_class = JobSerializer
