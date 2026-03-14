"""
Template tags for permission checks in templates.
Usage: {% load access_tags %}
       {% has_permission request.user 'can_delete_product' as can_delete %}
       {% if can_delete %}<button>Delete</button>{% endif %}
"""

from django import template
from apps.access.decorators import has_user_permission

register = template.Library()


@register.simple_tag
def has_permission(user, codename):
    """Check if user has the given permission codename."""
    return has_user_permission(user, codename)
