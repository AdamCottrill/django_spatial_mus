from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.urls import reverse


class Lake(models.Model):
    """
    A lookup table for lakes where fish were stocked, cwts either
    deployed or recovered, or where management/spatial units are located.
    """

    abbrev = models.CharField(max_length=2, unique=True)
    lake_name = models.CharField(max_length=30, unique=True)
    geom = models.MultiPolygonField(srid=4326, blank=True, null=True)

    # geom including associated watersheds
    # geom_plus = models.MultiPolygonField(srid=4326, blank=True, null=True)

    class Meta:
        ordering = ["abbrev"]

    def __str__(self):
        """String representation for a lake."""
        return "{} ({})".format(self.lake_name, self.abbrev)

    @property
    def label(self):
        """The name of the lake without 'Lake ..'.
        A shorter version of the lake name to save space when
        needed.
        """

        return self.lake_name.replace("Lake ", "")


class ManagementUnitType(models.Model):

    label = models.CharField(max_length=50)
    abbrev = models.SlugField(blank=True, unique=True, editable=False)
    description = models.CharField(max_length=300)

    # class Meta:
    #     ordering = ["abbrev"]

    def __str__(self):
        """String representation for management unit tyep."""
        return "{} ({})".format(self.label, self.abbrev)


class ManagementUnit(models.Model):
    """
    a class to hold geometries associated with arbitrary ManagementUnits that
    can be represented as polygons.  Examples include quota management units,
    assessment areas, statistical districts,  and lake trout rehabilitation
    zones.
    """

    label = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True, editable=False)
    description = models.CharField(max_length=300)
    geom = models.MultiPolygonField(srid=4326, blank=True, null=True)

    # centroid = models.PointField(srid=4326, blank=True, null=True)
    lake = models.ForeignKey(Lake, default=1, on_delete=models.CASCADE)
    mu_type = models.ForeignKey(ManagementUnitType, default=1, on_delete=models.CASCADE)

    primary = models.BooleanField(
        "Primary management unit type for this jurisdiction.",
        default=False,
        db_index=True,
    )

    class Meta:
        ordering = ["lake__abbrev", "mu_type", "label"]

    def get_slug(self):
        """
        the name is a concatenation of lake abbreviation, the managemnet unit
        type and and the management unit label.
        """

        lake = str(self.lake.abbrev)

        return slugify("_".join([lake, self.mu_type.abbrev, self.label]))

    def name(self):
        """
        returns the name of the management unit including the lake it
        is associated with, the management unit type and the label
        """
        return " ".join([str(self.lake), self.mu_type.abbrev.upper(), self.label])

    def __str__(self):
        return self.name()

    def save(self, *args, **kwargs):
        """
        Populate slug when we save the object.
        """
        # if not self.slug:
        self.slug = self.get_slug()
        super(ManagementUnit, self).save(*args, **kwargs)


class FN011(models.Model):
    """Project meta data."""

    lake = models.ForeignKey(Lake, related_name="projects", on_delete=models.CASCADE)

    year = models.CharField(max_length=4, db_index=True)
    prj_cd = models.CharField(max_length=13, db_index=True, unique=True)
    slug = models.SlugField(max_length=13, unique=True)
    prj_nm = models.CharField(max_length=255)
    prj_date0 = models.DateField()
    prj_date1 = models.DateField()

    comment0 = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-year", "-prj_date1"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.prj_cd)
        super(FN011, self).save(*args, **kwargs)

    def __str__(self):
        return "{} ({})".format(self.prj_nm, self.prj_cd)

    def fishnet_keys(self):
        """return the fish-net II key fields for this record"""
        return "{}".format(self.prj_cd)

    def get_absolute_url(self):
        return reverse("fn_portal:project_detail", args=[str(self.slug)])


class FN121(models.Model):
    """A table to hold information on fishing events/efforts"""

    management_units = models.ManyToManyField(
        ManagementUnit, related_name="fn121_samples", blank=True
    )

    project = models.ForeignKey(FN011, related_name="samples", on_delete=models.CASCADE)

    grtp = models.CharField(max_length=3, blank=True, null=True, db_index=True)
    gr = models.CharField(max_length=5, db_index=True, blank=True, null=True)

    slug = models.SlugField(max_length=100, unique=True)
    sam = models.CharField(max_length=5, db_index=True)
    effdt0 = models.DateField(blank=True, null=True, db_index=True)
    effdt1 = models.DateField(blank=True, null=True, db_index=True)
    effdur = models.FloatField(blank=True, null=True)
    efftm0 = models.TimeField(blank=True, null=True, db_index=True)
    efftm1 = models.TimeField(blank=True, null=True, db_index=True)
    effst = models.CharField(max_length=2, blank=True, null=True, db_index=True)

    orient = models.CharField(max_length=2, blank=True, null=True, db_index=True)
    sidep = models.FloatField(default=0, blank=True, null=True, db_index=True)
    secchi = models.FloatField(blank=True, null=True)

    site = models.CharField(max_length=100, blank=True, null=True)
    sitem = models.CharField(max_length=5, blank=True, null=True)
    dd_lat = models.FloatField(blank=True, null=True)
    dd_lon = models.FloatField(blank=True, null=True)

    geom = models.PointField(
        srid=4326, help_text="Represented as (longitude, latitude)"
    )
    comment1 = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ["project", "sam"]
        unique_together = ("project", "sam")

    def __str__(self):
        return self.slug.upper()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.fishnet_keys())
        # get all of the manamagent unit that our sample falls in and create the
        # appropriate associatedion>
        self.geom = Point(self.dd_lon, self.dd_lat)

        mus = ManagementUnit.objects.filter(geom__contains=self.geom)
        self.management_units.set(mus)
        super(FN121, self).save(*args, **kwargs)

    def fishnet_keys(self):
        """return the fish-net II key fields for this record"""
        return "{}-{}".format(self.project.prj_cd, self.sam)
