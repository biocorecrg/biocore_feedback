"""Template tags for biocore_feedback."""

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def biocore_feedback(context, app_name="Web App", api_url=None):
    """
    Render the <biocore-feedback> custom element and load the widget.js static script.
    Usage:
        {% load biocore_feedback %}
        {% biocore_feedback app_name="Genomics Apps" %}
    """
    request = context.get("request")
    if not api_url:
        try:
            api_url = reverse("biocore_feedback:submit")
        except Exception:
            api_url = "/api/feedback/"

    from django.templatetags.static import static
    script_url = static("biocore_feedback/widget.js")

    html = f"""<!-- Biocore Feedback Widget -->
<script src="{script_url}" defer></script>
<biocore-feedback app-name="{app_name}" api-url="{api_url}"></biocore-feedback>"""
    return mark_safe(html)
