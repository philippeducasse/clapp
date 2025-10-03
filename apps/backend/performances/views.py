from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework import status
from rest_framework import viewsets
from performances.models import Performance
from circus_agent_backend.serializers import PerformanceSerializer
from rest_framework.decorators import api_view


# class PerformanceViewSet(viewsets.ModelViewSet):
#     queryset = Performance.objects.all()
#     # Class used to convert JSON into Django Model objects and vice versa
@api_view(["GET"])
def get_user_performances(_request, user_id: int):
    all_user_performances = Performance.objects.filter(profile__id=user_id)

    serializer = PerformanceSerializer(all_user_performances, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
