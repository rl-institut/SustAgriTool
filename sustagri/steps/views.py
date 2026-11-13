from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods

from sustagri.projects.forms import *
from sustagri.steps.helpers import *
from sustagri.steps.survey import *

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


@require_http_methods(["GET", "POST"])
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


@require_http_methods(["GET", "POST"])
def site_conditions(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)
    step_id, step_info = get_step_id_and_info("site_conditions")

    # TODO: user handling
    # if (project.user != request.user) and (
    #     project.viewers.filter(user__email=request.user.email, share_rights="edit").exists() is False
    # ):
    #     raise PermissionDenied

    context = {
            "proj_id": proj_id,
            "step_id": step_id,
            "proj_name": project.name,
            "page_information": step_info,
            "step_list": step_list,
        }

    if request.method == "GET":
        timeseries = get_weather_data(proj_id, raw=False)
        logger.info("Got the timeseries")
        print(timeseries.keys())

        timeseries_labels = {
            "ghi": "Global Horizontal irradiance [W/m²]",
            "t_air": "Temperature [°C]",
            "t_dew": "Dewpoint Temperature[°C]",
            "windspeed": "Windspeed at 100 meters [m/s]",
            "fsr": "Forecast Surface Roughness (m)",
            "tp": "Precipitation [mm]",
            "e": "Evapotranspiration [mm]",
            "cf_aware": "Water Scarcity Footprint Factor [dimensionless]",
        }
        context.update(
            {
                # TODO: Retrieve timestamps from weather data directly or make project itself time aware
                # "timestamps": scenario.get_timestamps(json_format=True),
                "timeseries": json.dumps(timeseries),
                "timeseries_keys": timeseries_labels,
                "test": "test",
            }
        )

        # TODO: modify template, how to handle old css and js code?
        #   -> clarify visualization (plots) first!
        return render(request, "pages/site_conditions.html", context)

    if request.method == "POST":
        # TODO
        return HttpResponseRedirect(reverse("steps:ogp_steps", args=[proj_id, step_id + 1]))


@require_http_methods(["GET", "POST"])
def survey(request, proj_id):
    project = get_object_or_404(Project, id=proj_id)
    step_id, step_info = get_step_id_and_info("survey")

    if request.method == "POST":
        form = SurveyQuestionForm(request.POST, qs=SurveyAnswer.objects.filter(project_id=proj_id))

        if form.is_valid():
            qs = SurveyAnswer.objects.filter(project_id=proj_id)
            with open(f"project_{proj_id}_survey_answers.json", "w") as fp:
                json.dump(form.cleaned_data, fp, indent=4)
            for criteria_num, value in form.cleaned_data.items():
                crit = qs.get(question_id=criteria_num.replace("criteria_", ""))
                crit.value = json.dumps(value) if not isinstance(value, str) else value
                crit.save(update_fields=["value"])

            return HttpResponseRedirect(reverse("steps:ogp_steps", args=[proj_id, step_id + 1]))

    else:
        if proj_id is None:
            last_project_id = (
                SurveyAnswer.objects.all().values_list("proj_id", flat=True).distinct().order_by().last()
            )
            if last_project_id is None:
                last_project_id = 0
            project_id = last_project_id + 1
            return HttpResponseRedirect(reverse("view_survey", args=[project_id]))
        else:
            project_id = proj_id

            # Check if answers already exists, if not create them
            qs_answer = SurveyAnswer.objects.filter(project_id=project_id)
            create_new_form = False
            if qs_answer.exists():
                try:
                    form = SurveyQuestionForm(qs=qs_answer)
                # Could be caused by outdated survey answers
                except ObjectDoesNotExist:
                    create_new_form = True
                    pass
            else:
                create_new_form = True

            if create_new_form:
                questions = SurveyQuestion.objects.all()
                print(questions)
                for question in questions:
                    # print(question)
                    answer_param = {}
                    answer_param["project_id"] = project_id
                    answer_param["question"] = question
                    new_answer = SurveyAnswer(**answer_param)
                    new_answer.save()
                qs_answer = SurveyAnswer.objects.filter(project_id=project_id)

                import pdb; pdb.set_trace()
                form = SurveyQuestionForm(qs=qs_answer)

    categories = [cat for cat in SURVEY_QUESTIONS_CATEGORIES.keys()]
    categories_map = []
    matrix_headers = {}
    matrix_labels = {}

    for field in form.fields:
        question_id = field.split("criteria_")[1]
        # TODO: could be done from models "category" attribute
        cat = SURVEY_CATEGORIES.get(question_id)
        # TODO: reassign cat after testing phase is over
        categories_map.append(cat)
        # TODO here one can know that the question
        if is_matrix_source(form.fields[field]):
            subs = []
            labels = []
            question = get_survey_question_by_id(SURVEY_STRUCTURE, question_id)
            for answer, subquestions in question["subquestion"].items():
                labels.append(answer)
                for sq_id in subquestions:
                    q_main_id = ".".join(sq_id.split(".")[:2])
                    subquestion = get_survey_question_by_id(SURVEY_STRUCTURE, sq_id)
                    # print(subquestion)
                    if subquestion.get("display_type", "") == "matrix":
                        if subquestion["question"] not in subs:
                            subs.append(subquestion["question"])
            matrix_headers[field] = subs
            matrix_labels[field] = labels


    # Check which categories have field errors, so we can display them as open in the accordeon and the user can see the issue
    faulty_fields = [k.replace("criteria_", "") for k in form.errors.keys()]
    faulty_fields_cat = [SURVEY_CATEGORIES.get(q) for q in faulty_fields]
    faulty_fields_cat = set(faulty_fields_cat)


    return render(
        request,
        "pages/survey.html",
        {
            "form": form,
            "categories_map": categories_map,
            "categories": categories,
            "categories_verbose": SURVEY_QUESTIONS_CATEGORIES,
            "faulty_fields_cat": faulty_fields_cat,
            "matrix_headers": matrix_headers,
            "matrix_labels": matrix_labels,
            "proj_id": proj_id,
            "proj_name": project.name,
            "step_id": step_id,
            "step_list": step_list,
            "page_information": step_info,
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


