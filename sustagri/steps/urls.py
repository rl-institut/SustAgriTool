from django.urls import path

from .views import *

app_name = "steps"

urlpatterns = [
    path(
        "<int:proj_id>/edit/step/<int:step_id>",
        steps,
        name="ogp_steps",
    ),

    path(
        "project_information/<int:proj_id>",
        project_information,
        name="project_information",
    ),

    path(
        "site_conditions/<int:proj_id>",
        site_conditions,
        name="site_conditions",
    ),

    path(
        "survey/<int:proj_id>",
        survey,
        name="survey",
    ),
]
