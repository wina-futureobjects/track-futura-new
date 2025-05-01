from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

# Create your views here.
class ReportViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for reports.
    """
    def list(self, request):
        return Response({"message": "Reports list endpoint"})
    
    def retrieve(self, request, pk=None):
        return Response({"message": f"Report detail for {pk}"})
