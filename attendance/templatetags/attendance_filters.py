from django import template

register = template.Library()

@register.filter
def filter_status(attendance_records, status):
    """
    Filter attendance records by status.
    Usage in template: {{ attendance_records|filter_status:"Present" }}
    """
    return [record for record in attendance_records if record.status == status]

@register.filter
def get_item(dictionary, key):
    """
    Custom template filter to access dictionary items by key
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key) 