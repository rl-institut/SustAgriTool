from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your views here.
STEPS = {
    "project_information": _("Project Information"),
    "site_conditions": _("Site Conditions"),
    "survey": _("Survey"),
    # "agroforestry_practices": _("Agroforestry Practices"),
    # "relevant_policies": _("Relevant Policies"),
    # "business_models": _("Business Models"),
    # "example_case_studies": _("Example Case Studies"),
}


def project_information(request, proj_id):
    return render(
        request,
        "pages/project_information.html",
        {
            "proj_id": proj_id,
            "step_id": 1,
            "proj_name": "Dummy Project",
            "page_information": "Project Information",
            "step_list": list(STEPS.values()),
        },
    )


def site_conditions(request, proj_id):
    return render(
        request,
        "pages/site_conditions.html",
        {
            "proj_id": proj_id,
            "step_id": 2,
            "proj_name": "Dummy Project",
            "page_information": "Site Conditions",
            "step_list": list(STEPS.values()),
        },
    )


def survey(request, proj_id):
    return render(
        request,
        "pages/survey.html",
        {
            "proj_id": proj_id,
            "step_id": 3,
            "proj_name": "Dummy Project",
            "page_information": "Survey",
            "step_list": list(STEPS.values()),
        },
    )


def steps(request, proj_id, step_id=None):
    if step_id is None:
        return HttpResponseRedirect(
            reverse("steps:ogp_steps", args=[proj_id, 1])
        )

    return HttpResponseRedirect(
        reverse(
            f"steps:{list(STEPS.keys())[step_id - 1]}",
            args=[proj_id],
        )
    )

