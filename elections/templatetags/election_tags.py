from django import template

register = template.Library()

@register.filter
def get_status_color(status):
    colors = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger'
    }
    return colors.get(status, 'secondary')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_status_display(nomination):
    status_display = {
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected'
    }
    return status_display.get(nomination.status, nomination.status)