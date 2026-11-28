import logging

from django.contrib import messages
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import reverse

from .models import Project

logger = logging.getLogger(__name__)


def projects_list(request, proj_id=None):
    combined_projects_list = (
        Project.objects.filter(user=request.user).order_by("date_created").reverse()
    )

    return render(
        request,
        "projects/project_display.html",
        {
            "project_list": combined_projects_list,
        },
    )


def project_create(request):
    project = Project.objects.create(user=request.user)

    return HttpResponseRedirect(reverse("steps:project_information", args=[project.id]))


def project_duplicate(request, proj_id):
    project = get_object_or_404(Project, id=proj_id, user=request.user)

    # user handling?

    if request.method == "POST":
        model_data = project.export()
        new_project = Project(**model_data)
        new_project.save()

    return HttpResponseRedirect(
        reverse("projects:projects_list", args=[new_project.id]),
    )


def project_delete(request, proj_id):
    project = get_object_or_404(Project, id=proj_id, user=request.user)

    # if project.user != request.user:
    #     raise PermissionDenied

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project successfully deleted!")

    return HttpResponseRedirect(reverse("projects:projects_list"))
