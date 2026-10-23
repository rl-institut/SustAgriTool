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
    path(
        "agroforestry_practices/<int:proj_id>",
        agroforestry_practices,
        name="agroforestry_practices",
        ),
    path(
        "relevant_policies/<int:proj_id>",
        relevant_policies,
        name="relevant_policies",
    ),
    path(
        "business_models/<int:proj_id>",
        business_models,
        name="business_models",
    ),
    path(
        "example_case_studies/<int:proj_id>",
        example_case_studies,
        name="example_case_studies",
    ),
]
