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
    "agroforestry_practices": _("Agroforestry Practices"),
    "relevant_policies": _("Relevant Policies"),
    "business_models": _("Business Models"),
    "example_case_studies": _("Example Case Studies"),
}

step_list = list(STEPS.values())


def project_information(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)
    step_id, step_info = get_step_id_and_info("project_information")

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
            "page_information": step_info,
            "step_list": step_list,
            "form": form,
            "MAPBOX_ACCESS_TOKEN": settings.MAPBOX_ACCESS_TOKEN,
        },
    )


def site_conditions(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)
    step_id, step_info = get_step_id_and_info("site_conditions")

    return render(
        request,
        "pages/site_conditions.html",
        {
            "proj_id": proj_id,
            "step_id": step_id,
            "proj_name": project.name,
            "page_information": step_info,
            "step_list": step_list,
        },
    )


def survey(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)
    step_id, step_info = get_step_id_and_info("survey")

    return render(
        request,
        "pages/survey.html",
        {
            "proj_id": proj_id,
            "step_id": step_id,
            "proj_name": project.name,
            "page_information": step_info,
            "step_list": step_list,
        },
    )


def agroforestry_practices(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)
    step_id, step_info = get_step_id_and_info("agroforestry_practices")

    return render(
        request,
        "pages/agroforestry_practices.html",
        {
            "proj_id": proj_id,
            "step_id": step_id,
            "proj_name": project.name,
            "page_information": step_info,
            "step_list": step_list,
        },
    )


def relevant_policies(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)
    step_id, step_info = get_step_id_and_info("relevant_policies")

    return render(
        request,
        "pages/relevant_policies.html",
        {
            "proj_id": proj_id,
            "step_id": step_id,
            "proj_name": project.name,
            "page_information": step_info,
            "step_list": step_list,
        },
    )


def business_models(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)
    step_id, step_info = get_step_id_and_info("business_models")

    return render(
        request,
        "pages/business_models.html",
        {
            "proj_id": proj_id,
            "step_id": step_id,
            "proj_name": project.name,
            "page_information": step_info,
            "step_list": step_list,
        },
    )


def example_case_studies(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)
    step_id, step_info = get_step_id_and_info("example_case_studies")

    return render(
        request,
        "pages/example_case_studies.html",
        {
            "proj_id": proj_id,
            "step_id": step_id,
            "proj_name": project.name,
            "page_information": step_info,
            "step_list": step_list,
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

def get_step_id_and_info(step_name):
    step_id = int(list(STEPS.keys()).index(step_name) + 1)
    step_info = str(STEPS[step_name])
    return step_id, step_info


