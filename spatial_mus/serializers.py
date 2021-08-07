from rest_framework import serializers

from .models import FN011, FN121, Lake, ManagementUnit, ManagementUnitType


class LakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lake
        fields = ["id", "abbrev", "lake_name"]


class ManagementUnitTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementUnitType
        fields = ["id", "label", "abbrev", "description"]


class ManagementUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementUnit
        fields = [
            "id",
            "label",
            "slug",
            "description",
            "primary"
            # lake
            # mu_type
        ]


class FN011Serializer(serializers.ModelSerializer):
    class Meta:
        model = FN011
        fields = [
            "id",
            # lake,
            "year",
            "prj_cd",
            "slug",
            "prj_nm",
            "prj_date0",
            "prj_date1",
            "comment0",
        ]


class FN121Serializer(serializers.ModelSerializer):
    #mu/area will be dynamically added to serializer
    #
    class Meta:
        model = FN121
        fields = [
            "id",
            #project
            'grtp',
            'grm',
            'slug',
            'sam',
            'effdt0',
            'effdt1',
            'effdur',
            'efftm0',
            'efftm1',
            'effst',
            'orient',
            'sidep',
            'secchi',
            'site',
            'sitem ',
            'dd_lat',
            'dd_lon',
            'comment1'
            #geom
        ]



