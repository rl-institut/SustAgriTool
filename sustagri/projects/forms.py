import json
import logging

from django.forms import CharField
from django.forms import CheckboxSelectMultiple
from django.forms import ChoiceField
from django.forms import FloatField
from django.forms import Form
from django.forms import ModelForm
from django.forms import MultipleChoiceField
from django.forms import NumberInput
from django.forms import Textarea
from django.utils.html import format_html

from sustagri.steps.survey import SURVEY_STRUCTURE
from sustagri.steps.survey import TYPE_STRING

from .models import Project
from .models import SurveyQuestion

logger = logging.getLogger(__name__)


class ProjectForm(ModelForm):
    # CustomModelForm? check out offgridplanner
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "latitude",
            "longitude",
            "altitude",
        ]
        widgets = {
            "description": Textarea(attrs={"rows": 7}),
            "latitude": NumberInput(attrs={"x-model.number": "latitude"}),
            "longitude": NumberInput(attrs={"x-model.number": "longitude"}),
            "altitude": NumberInput(attrs={"x-model.number": "altitude"}),
        }
        help_texts = {
            "latitude": "Latitude coordinate "
            "of the project's location, in decimal degrees.",
            "longitude": "Longitude coordinate "
            "of the project's location, in decimal degrees.",
            "altitude": "Altitude of the project's "
            "location, in metres above sea level.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ("latitude", "longitude", "altitude"):
            self.fields[field].required = True


def is_matrix_source(field):
    return "matrix_source" in field.widget.attrs.get("class", "")


def get_survey_question_by_id(survey_questions, question_id):
    answer = None
    for q in survey_questions:
        if q["question_id"] == question_id:
            if answer is None:
                answer = q
            else:
                msg = f"Question number {question_id} appears multiple times"
                raise KeyError(msg)
    return answer


class SurveyQuestionForm(Form):
    def __init__(self, *args, **kwargs):  # noqa: C901, PLR0912, PLR0915
        self.qs_answers = kwargs.pop("qs", [])
        super().__init__(*args, **kwargs)
        for q in SURVEY_STRUCTURE:
            answer = self.qs_answers.get(question__question_id=q["question_id"])
            alv = answer.question.possible_answers
            label = answer.question.question
            if answer.question.description:
                label = format_html(
                    '{} <span class="icon icon-question cursor-help" title="{}">'
                    "</span>",
                    label,
                    answer.question.description,
                )
            opts = {"label": label}

            # by default the subquestion are not required
            if answer.question.subquestion_to is not None:
                opts["required"] = False

            if alv is not None:
                try:
                    possible_answers = json.loads(alv)
                    list_choices = [
                        (pa, pa.replace("_", " ").capitalize())
                        for pa in possible_answers
                    ]

                    if answer.question.multiple_answers is True:
                        opts["choices"] = list_choices
                        opts["widget"] = CheckboxSelectMultiple(
                            attrs={"class": "checkbox-grid"},
                        )
                        self.fields[f"criteria_{answer.question.id}"] = (
                            MultipleChoiceField(**opts)
                        )
                    else:
                        opts["choices"] = [("", "----------"), *list_choices]
                        self.fields[f"criteria_{answer.question.id}"] = ChoiceField(
                            **opts,
                        )
                except json.decoder.JSONDecodeError:
                    self.fields[f"criteria_{answer.question.id}"] = FloatField(**opts)
            elif answer.question.answer_type == TYPE_STRING:
                self.fields[f"criteria_{answer.question.id}"] = CharField(**opts)
            else:
                self.fields[f"criteria_{answer.question.id}"] = FloatField(**opts)
            # treat sub question differently:
            # - links to onchange of supra question
            # - hide the sub question if the supra question's answer is not "Yes"
            if answer.question.subquestion_to is not None:
                supra_question = SurveyQuestion.objects.get(
                    question_id=answer.question.subquestion_to.question_id,
                )

                # subquestion class
                self.fields[f"criteria_{answer.question.id}"].widget.attrs.update(
                    {"class": "sub_question"},
                )

                # subsubquestion class
                if supra_question.subquestion_to is not None:
                    if answer.question.matrix_answers is True:

                        def original_question_number(q_id):
                            answer = q_id
                            for letter in ("a", "b", "c", "d", "e"):
                                if letter in answer:
                                    answer = answer.replace(letter, "")
                            return answer

                        matrix_idxs = original_question_number(
                            answer.question.id,
                        ).replace(
                            f"{original_question_number(supra_question.id)}.",
                            "",
                        )
                        try:
                            matrix_col_idx, matrix_row_idx = matrix_idxs.split(".")
                        except ValueError:
                            logger.exception(
                                "Invalid matrix index %r for survey question %r",
                                matrix_idxs,
                                supra_question.pk,
                            )

                        self.fields[
                            f"criteria_{answer.question.id}"
                        ].widget.attrs.update(
                            {
                                "class": f"sub_question sub_sub_question matrix_target "
                                f"label_row_{int(matrix_row_idx) + 1} "
                                f"matrix_row_{int(matrix_row_idx) + 1} "
                                f"matrix_col_{int(matrix_col_idx) + 1}",
                            },
                        )
                        supra_question_css = self.fields[
                            f"criteria_{supra_question.id}"
                        ].widget.attrs["class"]
                        if "matrix_source" not in supra_question_css:
                            self.fields[f"criteria_{supra_question.id}"].widget.attrs[
                                "class"
                            ] = f"{supra_question_css} matrix_source"
                    else:
                        self.fields[
                            f"criteria_{answer.question.id}"
                        ].widget.attrs.update(
                            {"class": "sub_question sub_sub_question"},
                        )
                field = self.fields[f"criteria_{supra_question.id}"]
                if is_matrix_source(field):
                    # here we know we are within matrix questions
                    attr = {
                        "data-matrix-subquestion-mapping": supra_question.subquestion
                    }
                else:
                    attr = {"data-subquestion-mapping": supra_question.subquestion}
                field.widget.attrs.update(attr)

                # only provide initial value for subquestion if
                #   the answer to supraquestion exists and is valid
                supra_answer = self.qs_answers.get(question=supra_question)
                if supra_answer.value is not None:
                    if answer.value:
                        if answer.question.multiple_answers is True:
                            self.fields[
                                f"criteria_{answer.question.id}"
                            ].initial = json.loads(
                                answer.value.replace("'", '"'),
                            )
                        else:
                            self.fields[
                                f"criteria_{answer.question.id}"
                            ].initial = answer.value

            elif answer.value:
                if answer.question.multiple_answers is True:
                    self.fields[f"criteria_{answer.question.id}"].initial = json.loads(
                        answer.value.replace("'", '"'),
                    )
                else:
                    self.fields[f"criteria_{answer.question.id}"].initial = answer.value
