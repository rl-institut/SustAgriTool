import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from sustagri.projects.forms import *

logger = logging.getLogger(__name__)

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
    project = get_object_or_404(Project, id=proj_id)
    step_id = get_step_id("project_information")

    if request.POST:
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse("steps:ogp_steps", args=[proj_id, step_id + 1])
            )
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "pages/project_information.html",
        {
            "proj_id": proj_id,
            "step_id": step_id,
            "proj_name": project.name,
            "page_information": "Project Information",
            "step_list": list(STEPS.values()),
            "form": form,
            "MAPBOX_ACCESS_TOKEN": settings.MAPBOX_ACCESS_TOKEN,
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

def get_step_id(step_name):
    return list(STEPS.keys()).index(step_name) + 1

