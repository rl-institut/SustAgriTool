from django.db import models
from django.forms.models import model_to_dict
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

# TODO: move this elsewhere and adapt units
TIMESERIES_UNITS = (
    ("Wh", "Wh"),
    ("kWh", "kWh"),
    ("MWh", "MWh"),
    ("GWh", "GWh"),
    ("TWh", "TWh"),
)


class Project(models.Model):
    name = models.CharField(max_length=51, blank=True, default="")
    description = models.CharField(max_length=201, blank=True, default="")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    # options = models.ForeignKey(Options, on_delete=models.SET_NULL, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(default=None, null=True, blank=True)
    # economic data?

    def export(self):
        """
        following the export/import logic of WEFEgui/cpn in order to duplicate a project;
        this function may be extended to include more things (weather data, soil data, ...);
        then maybe a helper function is needed to properly generate the new project out of it
        """
        dm = model_to_dict(self, exclude=["id"])#, "user", "viewers"])
        return dm



class Timeseries(models.Model):
    name = models.CharField(max_length=120, blank=True, default="")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)

    # TODO: include user
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    values = ArrayField(models.FloatField(), blank=False, default=list([]))
    units = models.CharField(max_length=50, choices=TIMESERIES_UNITS, blank=True, null=True)

    start_time = models.DateTimeField(blank=True, default=None, null=True)
    end_time = models.DateTimeField(blank=True, default=None, null=True)
    time_step = models.IntegerField(blank=True, default=None, null=True, validators=[MinValueValidator(1)])

