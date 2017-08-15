from django import template

register = template.Library()


@register.filter
def bs_alert(messages, tag):
    result = ""
    tag_messages = []
    for message in messages:
        if message.tags == tag:
            tag_messages.append(message)
    if tag_messages:
        result += '<div class="alert alert-{0}">'.format(tag if tag != "error" else "danger")
        result += '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'
        for message in tag_messages:
            result += '<p>{0}</p>'.format(message)
        result += '</div>'
    return result

@register.filter
def add_css_class(field, add_class):
    old_class = field.field.widget.attrs.get("class", None)
    new_class = old_class + " " + add_class if old_class else add_class
    return field.as_widget(attrs = {"class": new_class})

