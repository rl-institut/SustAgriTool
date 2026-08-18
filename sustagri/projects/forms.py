from django.forms import ModelForm
from django.forms import Textarea

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
        widgets = {"description": Textarea(attrs={"rows": 7})}
