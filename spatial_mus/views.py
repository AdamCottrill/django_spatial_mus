# from django.shortcuts import render
from rest_framework import generics

from spatial_mus.models import ManagementUnit

from .models import FN011, FN121, ManagementUnit, ManagementUnitType
from .serializers import (FN011Serializer, FN121Serializer,
                          ManagementUnitSerializer,
                          ManagementUnitTypeSerializer)


class ManagementUnitTypeList(generics.ListAPIView):
    queryset = ManagementUnitType.objects.all()
    serializer_class = ManagementUnitTypeSerializer


class ManagementUnitList(generics.ListAPIView):
    #filter by lake, mu_type, primary
    queryset = ManagementUnit.objects.all()
    serializer_class = ManagementUnitSerializer


class FN011List(generics.ListAPIView):
    #filter by:
    #  mu - all in, some points in
    #  roi - all in, some points in

    queryset = FN011.objects.all()
    serializer_class = FN011Serializer


class FN121List(generics.ListAPIView):
    # filter by mu, year, prj_cd, prj_cd__like, roi
    queryset = FN121.objects.all()
    serializer_class = FN121Serializer
