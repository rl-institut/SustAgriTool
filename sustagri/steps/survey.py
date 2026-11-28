import copy
import functools
import logging

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

# ----- general assignments for survey question format and answer processing
TYPE_STRING = "string"
TYPE_FLOAT = "float"

INFOBOX = "description"
# TODO: INFOBOX not yet working as intended

TYPE_ONE = "type1"
TYPE_TWO = "type2"
# TODO: next to general assignment "TYPE",
#   there are variables which are more question specific
#   -> confirm if we need all of that


# ----- functions to duplicate questions based on different cases ------
# TODO: not yet implemented, may not be required
def set_question_suffix(q_id, suffix):
    """Format question when suffix is used

    :param q_id: question ID
    :param suffix: suffix to prepend
    :return: example q_id="5.1" and suffix="_DS" --> 5_DS.1
    """
    tot = q_id.split(".")
    base_sections = 2
    main_id = tot[0]
    if len(tot) >= base_sections:
        rest = tot[1:]

        answer = main_id + suffix + "." + ".".join(rest)
    else:
        answer = main_id + suffix
    return answer


def generate_generic_questions(
    suffixes,
    survey_questions_template=None,
    text_to_replace=None,
):
    """Generate redundant question for different cases
    :param suffixes: dict mapping of label to subquestion suffix
    :param survey_questions_template: the redundant questions which
        need to be duplicated for each suffix mapping
    :param text_to_replace: the text placeholder which will be
        replaced by the `suffices` keys
    :return: list of survey questions
    """
    if not survey_questions_template:
        survey_questions_template = []

    new_questions = []
    for name, suffix in suffixes.items():
        temp = copy.deepcopy(survey_questions_template)
        for question in temp:
            if text_to_replace is not None:
                question["question"] = question["question"].replace(
                    text_to_replace,
                    name,
                )
            question_id = question["question_id"]

            # generate new id based on the suffix
            question["question_id"] = set_question_suffix(question_id, suffix)
            subquestions = question.get("subquestion", {})
            for subq in subquestions:
                subq_id = subquestions[subq]
                if isinstance(subq_id, str):
                    subq_id = [subq_id]

                # generate new ids for the subquestions based on the suffix
                new_ids = [set_question_suffix(q_id, suffix) for q_id in subq_id]
                if len(new_ids) == 1:
                    new_ids = new_ids[0]
                subquestions[subq] = new_ids
            if subquestions:
                question["subquestion"] = subquestions
            new_questions.append(question)
    return new_questions


# ----- functions to create matrix questions ------


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


def get_survey_question_index(survey_questions, question):
    if isinstance(question, dict):
        q_id = question["question_id"]
    elif isinstance(question, str):
        q_id = question

    q_idx = None
    for i, q in enumerate(survey_questions):
        if q["question_id"] == q_id:
            q_idx = i
    return q_idx


def remove_question(survey_questions, question):
    q_id = question["question_id"]
    q_idx = None
    for i, q in enumerate(survey_questions):
        if q["question_id"] == q_id:
            q_idx = i
    if q_idx is not None:
        return survey_questions.pop(q_idx)

    return None


def get_shared_subquestions(subquestions):
    shared_subquestions_mapping = {}

    for k, v in subquestions.items():
        if not isinstance(v, list):
            vals = v if isinstance(v, list) else [v]
        for sq in vals:
            if sq in shared_subquestions_mapping:
                shared_subquestions_mapping[sq].append(k)
            else:
                shared_subquestions_mapping[sq] = [k]

    return {k: v for k, v in shared_subquestions_mapping.items() if len(v) > 1}


def compare_matrix_questions(q1, q2):
    return int(q1["question_id"].split(".")[-1]) - int(q2["question_id"].split(".")[-1])


def generate_matrix_questions(survey_questions, text_to_replace):
    extra_questions = {}
    extra_questions_size = {}
    for _qi, q in enumerate(survey_questions):
        if (
            q.get("display_type", "") == "multiple_choice_tickbox"
            and "subquestion" in q
        ):
            extra_number = 0
            sq = q["subquestion"]
            # get the list of question's answers which
            #   share the same link to a subquestion
            shared_subquestions = get_shared_subquestions(sq)
            # for each subquestion, if this one has the display
            #   type 'matrix', we will make as many copies of it
            # as there are question's answer with a link to the subquestion
            for ssq_id in shared_subquestions:
                ssq = get_survey_question_by_id(survey_questions, ssq_id)
                if ssq.get("display_type", "") == "matrix":
                    extra_questions[ssq_id] = []
                    for suffix, supra_answer in enumerate(shared_subquestions[ssq_id]):
                        temp = copy.deepcopy(ssq)
                        temp["question"] = temp["question"].replace(
                            text_to_replace,
                            supra_answer,
                        )
                        temp["question_id"] = ssq_id + "." + str(suffix)
                        # Replace the subquestion id in the supraquestion subquestions
                        if isinstance(q["subquestion"][supra_answer], str):
                            q["subquestion"][supra_answer] = temp["question_id"]
                        else:
                            q["subquestion"][supra_answer][
                                q["subquestion"][supra_answer].index(ssq_id)
                            ] = temp["question_id"]
                        extra_questions[ssq_id].append(temp)
                    # update the number of extra questions
                    extra_number += len(extra_questions[ssq_id])
                if extra_number > 0:
                    extra_questions_size[q["question_id"]] = extra_number

    for q_id, value in extra_questions.items():
        # find the original question index in the survey questions
        q_idx = get_survey_question_index(survey_questions, q_id)
        # insert the matrix subquestions
        survey_questions = (
            survey_questions[: q_idx + 1] + value + survey_questions[q_idx + 1 :]
        )
        # remove the original question from the survey questions
        survey_questions.pop(q_idx)

    # sort the matrix questions by rows instead of by columns
    #   (only for display purposes)
    for q_id, value in extra_questions_size.items():
        q_idx = survey_questions.index(
            get_survey_question_by_id(survey_questions, q_id),
        )
        col_sorted_questions = survey_questions[q_idx + 1 : q_idx + 1 + value]
        row_sorted_questions = sorted(
            col_sorted_questions,
            key=functools.cmp_to_key(compare_matrix_questions),
        )
        survey_questions[q_idx + 1 : q_idx + 1 + extra_questions_size[q_id]] = (
            row_sorted_questions
        )

    return survey_questions


# ----- different sections of the survey, combined in SURVEY_STRUCTURE ------
BASIC_QUESTION_STRUCTURE = [
    {
        "question": "To be or not to be?",
        INFOBOX: "Important question. Choose wisely. "
        "There will be no mapping to this question. "
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
        INFOBOX: "Please select at least one option. "
        "This question will be mapped to a TYPE and it has subquestions",
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
        "variable_name": "variable_one",  # Do we need variables?
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

# TODO: this should be implemented once we know
#   it's needed and how exactly it's going to look like
GENERIC_QUESTION_STRUCTURE = []

MATRIX_QUESTION_STRUCTURE = [
    {
        "question": "Do you want a matrix question?",
        "question_id": "42",
        "possible_answers": ["Yes", "No"],
        "subquestion": {"Yes": ["43", "51"]},
        INFOBOX: "Some info about the matrix question.",
    },
    *generate_matrix_questions(
        survey_questions=[
            {
                "question": "Which rows do you want for your matrix?",
                "question_id": "43",
                "possible_answers": [
                    "col1",
                    "col2",
                ],
                "answer_map_to": TYPE_ONE,
                "display_type": "multiple_choice_tickbox",
                "subquestion": {
                    "col1": ["43.1", "43.2"],
                    "col2": ["43.1", "43.2"],
                },
            },
            {
                "question": "How do you like the first row on a scale from 0 to 9? "
                "Look at [TEXT_TO_REPLACE]",
                "question_id": "43.1",
                "variable_name": "variable_431",
                "possible_answers": TYPE_FLOAT,
                "answer_map_to": TYPE_TWO,
                "display_type": "matrix",
            },
            {
                "question": "And the one related to [TEXT_TO_REPLACE]?",
                INFOBOX: "Note that there is some [TEXT_TO_REPLACE]!",
                "question_id": "43.2",
                "variable_name": "variable_2000",
                "possible_answers": TYPE_FLOAT,
                "answer_map_to": TYPE_TWO,
                "display_type": "matrix",
            },
        ],
        text_to_replace="TEXT_TO_REPLACE",
        # TODO: text_to_replace duplicates questions? needs some fine-tuning
    ),
]


SURVEY_STRUCTURE = (
    BASIC_QUESTION_STRUCTURE + GENERIC_QUESTION_STRUCTURE + MATRIX_QUESTION_STRUCTURE
)


# ----- assign different categories to different sections of the survey ------
CATEGORY_ONE = "category1"
CATEGORY_TWO = "category2"
SURVEY_QUESTIONS_CATEGORIES = {
    CATEGORY_ONE: _("Category 1: Basics"),
    CATEGORY_TWO: _("Category 2: Matrix"),
}


def infer_survey_categories():
    question_category_map = {}
    for category, question_list in zip(
        (CATEGORY_ONE, CATEGORY_TWO),
        (
            BASIC_QUESTION_STRUCTURE,
            MATRIX_QUESTION_STRUCTURE,
        ),
        # TODO: verify strict=False, it is based on the assumption that
        #  one category for two structures should be possible
        strict=False,
    ):
        for question in question_list:
            question_category_map[question["question_id"]] = category
    return question_category_map


SURVEY_CATEGORIES = infer_survey_categories()


# ----- assign subquestions to their parent questions ------


def collect_subquestion_mapping():
    subquestion_mapping = {}
    for question in SURVEY_STRUCTURE:
        subquestions = question.get("subquestion", {})
        for possible_answer, subq in subquestions.items():
            if isinstance(subq, list):
                for sq in subq:
                    if sq not in subquestion_mapping:
                        # I used tuples to pass possible_answer alongside the
                        #   question_id, due to json converting this will
                        #   turn out as a list...use list right away
                        subquestion_mapping[sq] = [
                            question["question_id"],
                            possible_answer,
                        ]
                    # some subquestions produce the error,
                    #   but seem to be dumped correctly in the json file!
                    elif subquestion_mapping[sq] != [
                        question["question_id"],
                        possible_answer,
                    ]:
                        logger.debug("Problem with subquestion: %s", sq)

            elif subq not in subquestion_mapping:
                subquestion_mapping[subq] = [question["question_id"], possible_answer]
            elif subquestion_mapping[subq] != [
                question["question_id"],
                possible_answer,
            ]:
                if question["question_id"] in subquestion_mapping[subq]:
                    subquestion_mapping[subq] = [question["question_id"], ""]
                else:
                    logger.debug("Problem with subquestion: %s", subq)

    return subquestion_mapping


SUB_QUESTION_MAPPING = collect_subquestion_mapping()
