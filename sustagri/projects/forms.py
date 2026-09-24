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
