from django.forms import *
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import *

### --- survey stuff --- ###
# TODO: Decide where this belongs, maybe even put everything survey-related (and weather data related) to /steps/
TYPE_STRING = "string"
TYPE_FLOAT = "float"

INFOBOX = "description"
TYPE_ONE = "type1"
TYPE_TWO = "type2"

SURVEY_STRUCTURE = [
        {
            "question": "To be or not to be?",
            INFOBOX: "Important question. Choose wisely. There will be no mapping to this question. "
                     "However, your answer can be processed anyway.",
            "question_id": "1",
            "possible_answers": ["To be", "Not to be"],
        },
        {
            "question": "What do you want to be?",
            "question_id": "2",
            "possible_answers": [
                "something",
                "something else",
                "unicorn",
            ],
            INFOBOX: "Please select at least one option. This question will be mapped to a TYPE and it has subquestions",
            "answer_map_to": TYPE_ONE,
            "display_type": "multiple_choice_tickbox",
            "subquestion": {
                "something": "2.1",
                "something else": ["2.2", "2.3"],
            },
        },
        {
            "question": "How much?",
            "question_id": "2.1",
            "variable_name": "variable_one",        # Do we need variables?
            "possible_answers": TYPE_FLOAT,
            "answer_map_to": TYPE_TWO,
        },
        {
            "question": "What else?",
            "question_id": "2.2",
            "variable_name": "variable_two",
            "possible_answers": TYPE_STRING,
            "answer_map_to": TYPE_TWO,
        },
        {
            "question": "How many?",
            "question_id": "2.3",
            "variable_name": "variable_one",
            "possible_answers": TYPE_FLOAT,
            "answer_map_to": TYPE_TWO,
        },
    ]


CATEGORY_ONE = "category1"
SURVEY_QUESTIONS_CATEGORIES = {
    CATEGORY_ONE: _("Category 1"),
}

def infer_survey_categories():
    question_category_map = {}
    for category, question_list in zip(
        CATEGORY_ONE,
        SURVEY_STRUCTURE,
        ):
        for question in question_list:
            question_category_map[question["question_id"]] = category
    return question_category_map

SURVEY_CATEGORIES = infer_survey_categories()


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
        widgets = {
            "description": Textarea(attrs={"rows": 7}),
            "latitude": NumberInput(attrs={"x-model.number": "latitude"}),
            "longitude": NumberInput(attrs={"x-model.number": "longitude"}),
            "altitude": NumberInput(attrs={"x-model.number": "altitude"}),
            }
        help_texts = {
            "latitude": "Latitude coordinate of the project's location, in decimal degrees.",
            "longitude": "Longitude coordinate of the project's location, in decimal degrees.",
            "altitude": "Altitude of the project's location, in metres above sea level.",
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
    def __init__(self, *args, **kwargs):
        self.qs_answers = kwargs.pop("qs", [])
        super().__init__(*args, **kwargs)
        for q in SURVEY_STRUCTURE:
            answer = self.qs_answers.get(question__question_id=q["question_id"])
            alv = answer.question.possible_answers
            label = answer.question.question
            if answer.question.description:
                question_icon = f'<span class="icon icon-question" data-bs-toggle="tooltip" title="{answer.question.description}"></span>'
                label += question_icon

            opts = {"label": format_html(f"{label}")}

            # by default the subquestion are not required
            if answer.question.subquestion_to is not None:
                opts["required"] = False

            if alv is not None:
                try:
                    possible_answers = json.loads(alv)
                    list_choices = [(pa, pa.replace("_", " ").capitalize()) for pa in possible_answers]

                    if answer.question.multiple_answers is True:
                        opts["choices"] = list_choices
                        opts["widget"] = CheckboxSelectMultiple(attrs={"class": "checkbox-grid"})
                        self.fields[f"criteria_{answer.question.id}"] = MultipleChoiceField(**opts)
                    else:
                        opts["choices"] = [("", "----------")] + list_choices
                        self.fields[f"criteria_{answer.question.id}"] = ChoiceField(**opts)
                except json.decoder.JSONDecodeError:
                    self.fields[f"criteria_{answer.question.id}"] = FloatField(**opts)
            else:
                if answer.question.answer_type == TYPE_STRING:
                    self.fields[f"criteria_{answer.question.id}"] = CharField(**opts)
                else:
                    self.fields[f"criteria_{answer.question.id}"] = FloatField(**opts)
            # treat sub question differently:
            # - links to onchange of supra question
            # - hide the sub question if the supra question's answer is not "Yes"
            if answer.question.subquestion_to is not None:

                supra_question = SurveyQuestion.objects.get(question_id=answer.question.subquestion_to.question_id)

                # subquestion class
                self.fields[f"criteria_{answer.question.id}"].widget.attrs.update({"class": "sub_question"})

                # subsubquestion class
                if supra_question.subquestion_to is not None:
                    if answer.question.matrix_answers is True:
                        # import pdb;pdb.set_trace()
                        def original_question_number(q_id):
                            answer = q_id
                            for letter in ("a", "b", "c", "d", "e"):
                                if letter in answer:
                                    answer = answer.replace(letter, "")
                            return answer

                        matrix_idxs = original_question_number(answer.question.id).replace(
                            f"{original_question_number(supra_question.id)}.", ""
                        )
                        try:
                            matrix_col_idx, matrix_row_idx = matrix_idxs.split(".")
                        except:
                            print(supra_question.__dict__)
                            print(matrix_idxs)

                        self.fields[f"criteria_{answer.question.id}"].widget.attrs.update(
                            {
                                "class": f"sub_question sub_sub_question matrix_target label_row_{int(matrix_row_idx)+1} matrix_row_{int(matrix_row_idx)+1} matrix_col_{int(matrix_col_idx)+1}"
                            }
                        )
                        # self.fields[f"criteria_{answer.question.id}"].widget.attrs.update({"class": f"sub_question sub_sub_question matrix_target matrix_col_{int(matrix_col_idx)+1}"})
                        supra_question_css = self.fields[f"criteria_{supra_question.id}"].widget.attrs["class"]
                        if "matrix_source" not in supra_question_css:
                            self.fields[f"criteria_{supra_question.id}"].widget.attrs[
                                "class"
                            ] = f"{supra_question_css} matrix_source"
                    else:
                        self.fields[f"criteria_{answer.question.id}"].widget.attrs.update(
                            {"class": "sub_question sub_sub_question"}
                        )
                if is_matrix_source(self.fields[f"criteria_{supra_question.id}"]):
                    # here we know we are within matrix questions
                    self.fields[f"criteria_{supra_question.id}"].widget.attrs.update(
                        {
                            "onchange": f"triggerMatrixSubQuestion(new_value=this,subQuestionMapping={supra_question.subquestion})"
                        }
                    )
                else:

                    self.fields[f"criteria_{supra_question.id}"].widget.attrs.update(
                        {
                            "onchange": f"triggerSubQuestion(new_value=this,subQuestionMapping={supra_question.subquestion})"
                        }
                    )

                # only provide initial value for subquestion if the answer to supraquestion exists and is valid
                supra_answer = self.qs_answers.get(question=supra_question)
                if supra_answer.value is not None:
                    if answer.value:
                        if answer.question.multiple_answers is True:
                            self.fields[f"criteria_{answer.question.id}"].initial = json.loads(
                                answer.value.replace("'", '"')
                            )
                        else:
                            self.fields[f"criteria_{answer.question.id}"].initial = answer.value

            else:
                if answer.value:
                    if answer.question.multiple_answers is True:
                        self.fields[f"criteria_{answer.question.id}"].initial = json.loads(
                            answer.value.replace("'", '"')
                        )
                    else:
                        self.fields[f"criteria_{answer.question.id}"].initial = answer.value
