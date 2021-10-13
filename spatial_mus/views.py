# from django.shortcuts import render
from django.db.models import Prefetch
from rest_framework import generics, pagination


from .models import FN011, FN121, ManagementUnit, ManagementUnitType
from .serializers import (
    FN011Serializer,
    FN121Serializer,
    ManagementUnitSerializer,
    ManagementUnitTypeSerializer,
)


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000

class ManagementUnitTypeList(generics.ListAPIView):
    queryset = ManagementUnitType.objects.all()
    serializer_class = ManagementUnitTypeSerializer


class ManagementUnitList(generics.ListAPIView):
    # filter by lake, mu_type, primary
    queryset = ManagementUnit.objects.all()
    serializer_class = ManagementUnitSerializer


class FN011List(generics.ListAPIView):
    # filter by:
    #  mu - all in, some points in
    #  roi - all in, some points in

    queryset = FN011.objects.all()
    serializer_class = FN011Serializer


class FN121List(generics.ListAPIView):
    # filter by mu, year, prj_cd, prj_cd__like, roi
    serializer_class = FN121Serializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        """Prefetch the appropriate management units depending on the value of
        mu_type. If mu_type is null, use default management unit type (which can
        be different by lake.  Defer the management unit geom field - we don't
        need here and it is expensive to deal with."""

        mu_type = self.request.query_params.get("mu_type")
        year = self.request.query_params.get("year", "2010")
        if mu_type:
            mus = ManagementUnit.objects.filter(mu_type__abbrev=mu_type).defer("geom")
        else:
            mus = ManagementUnit.objects.filter(primary=True).defer("geom")

        prefetch = Prefetch("management_units", queryset=mus, to_attr="mu")
        queryset = (
            FN121.objects.select_related("project")
            .prefetch_related(prefetch)
            .filter(project__year=year)
            .all()
        )
        return queryset
