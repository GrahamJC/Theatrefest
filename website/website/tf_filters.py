from django import template

register = template.Library()


@register.filter
def add_css_class(field, add_class):
    old_class = field.field.widget.attrs.get("class", None)
    new_class = old_class + " " + add_class if old_class else add_class
    return field.as_widget(attrs = {"class": new_class})

