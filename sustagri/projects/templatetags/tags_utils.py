from django import template

register = template.Library()


@register.filter(name="fill_spaces")
def fill_spaces(string: str):
    return string.replace(" ", "_")


@register.simple_tag
def setvar(val=None):
    return val


@register.filter
def getval(val):
    return str(val)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_field(form, key):
    return form.fields[key].get_bound_field(form, key)


@register.filter
def has_field(form, key):
    return key in form.fields


@register.filter
def get_index(a_list, index):
    return a_list[index]


@register.filter
def is_current_category(field_category, current_category):
    return field_category == current_category


@register.filter
def is_subquestion(field):
    field_classes = field.field.widget.attrs.get("class")
    answer = False
    if field_classes is not None:
        if "sub_question" in field_classes:
            answer = True
    return answer


@register.filter
def is_subsubquestion(field):
    field_classes = field.field.widget.attrs.get("class")
    answer = False
    if field_classes is not None:
        if "sub_sub_question" in field_classes:
            answer = True
    return answer


@register.filter
def is_matrix(field):
    field_classes = field.field.widget.attrs.get("class")
    answer = False
    if field_classes is not None:
        if "matrix_target" in field_classes:
            answer = True
    return answer


@register.filter
def is_matrix_source(field):
    field_classes = field.field.widget.attrs.get("class")
    answer = False
    if field_classes is not None:
        if "matrix_source" in field_classes:
            answer = True
    return answer
