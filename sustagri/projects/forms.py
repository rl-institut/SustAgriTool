from django.forms import ModelForm, Textarea, NumberInput

from .models import *

class ProjectForm(ModelForm):
    # CustomModelForm? check out offgridplanner
    class Meta:
        model = Project
        exclude = [
            "date_created",
            "date_updated",
            "user",
            "options",
        ]
        widgets = {
            "description": Textarea(attrs={"rows": 7}),
            "latitude": NumberInput(attrs={"x-model.number": "latitude"}),
            "longitude": NumberInput(attrs={"x-model.number": "longitude"}),
            "altitude": NumberInput(attrs={"x-model.number": "altitude"}),
            }
        help_texts = {
            "latitude": "Latitude coordinate of the project's location, in decimal degrees.",
            "longitude": "Longitude coordinate of the project's location, in decimal degrees.",
            "altitude": "Altitude of the project's location, in metres above sea level.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ("latitude", "longitude", "altitude"):
            self.fields[field].required = True
