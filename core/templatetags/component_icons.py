from django import template

register = template.Library()

@register.inclusion_tag('core/component_icon.html')
def component_icon(repo):
    """
    Template tag to render a component with appropriate icon based on repo slug/name.
    Usage: {% component_icon repo %}
    """
    return {'repo': repo}
