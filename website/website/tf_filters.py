from django import template

register = template.Library()


def create_bs_alert(messages, type):
    html = ""
    if messages:
        html += '<div class="alert alert-{0}" role="alert">'.format(type)
        html += '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'
        for message in messages:
            html += "<p>{0}</p>".format(message)
        html += '</div>'
    return html


@register.filter
def bs_alerts(alerts):
    html = ""
    if alerts:
        if 'error' in alerts:
            html += create_bs_alert(alerts['error'], "danger")
        if 'warning' in alerts:
            html += create_bs_alert(alerts['warning'], "warning")
        if 'success' in alerts:
            html += create_bs_alert(alerts['success'], "success")
        if 'info' in alerts:
            html += create_bs_alert(alerts['info'], "info")
    return html


