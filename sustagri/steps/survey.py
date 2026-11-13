from django.utils.translation import gettext_lazy as _

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
        (CATEGORY_ONE,),
        (SURVEY_STRUCTURE,),
        ):
        for question in question_list:
            question_category_map[question["question_id"]] = category
    return question_category_map

SURVEY_CATEGORIES = infer_survey_categories()
