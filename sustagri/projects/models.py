from django.db import models
from django.forms.models import model_to_dict


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

