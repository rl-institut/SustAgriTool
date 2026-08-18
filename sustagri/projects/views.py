import logging

from django.shortcuts import *
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .forms import *

logger = logging.getLogger(__name__)


def projects_list(request, proj_id=None):
    combined_projects_list = (
        # Project.objects.filter(Q(user=request.user) | Q(viewers__user__email=request.user.email))
        Project.objects
        # .distinct()
        .order_by("date_created")
        .reverse()
    )

    # scenario_upload_form = UploadFileForm(labels=dict(name=_("New scenario name"), file=_("Scenario file")))
    # project_upload_form = UploadFileForm(labels=dict(name=_("New project name"), file=_("Project file")))
    # project_share_form = ProjectShareForm()
    # project_revoke_form = ProjectRevokeForm(proj_id=proj_id)
    # usecase_form = UseCaseForm(usecase_qs=UseCase.objects.all(), usecase_url=reverse("usecase_search"))

    return render(
        request,
        "projects/project_display.html",
        {
            "project_list": combined_projects_list,
            # "proj_id": proj_id,
            # "scenario_upload_form": scenario_upload_form,
            # "project_upload_form": project_upload_form,
            # "project_share_form": project_share_form,
            # "project_revoke_form": project_revoke_form,
            # "usecase_form": usecase_form,
            # "translated_text": {
            #     "showScenarioText": _("Show scenarios"),
            #     "hideScenarioText": _("Hide scenarios"),
            # },
        },
    )


def project_create(request):
    if request.POST:
        form = ProjectForm(request.POST)
        if form.is_valid():
            logger.info(f"Creating new project")
            project = Project.objects.create(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                longitude=form.cleaned_data["longitude"],
                latitude=form.cleaned_data["latitude"],
                # user=request.user,
            )
            return HttpResponseRedirect(reverse("steps:project_information", args=[project.id]))
    else:
        form = ProjectForm()
    return render(request, "projects/project_create.html", {"form": form})


def project_delete(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)

    # if project.user != request.user:
    #     raise PermissionDenied

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project successfully deleted!")

    return HttpResponseRedirect(reverse("project_search"))
