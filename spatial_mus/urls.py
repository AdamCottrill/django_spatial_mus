from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path("management_unit_types/", views.ManagementUnitTypeList.as_view()),
    path("management_units/", views.ManagementUnitList.as_view()),
    path("projects/", views.FN011List.as_view()),
    path("samples/", views.FN121List.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
