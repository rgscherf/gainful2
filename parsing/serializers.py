from parsing.models import Job
from rest_framework import serializers

class JobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ("organization", "title", "division", "url_detail", "date_closing", "salary_waged", "salary_amount", "region", "date_posted")
