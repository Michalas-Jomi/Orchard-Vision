from django.template.defaultfilters import escape
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import template


register = template.Library()

@register.filter
def model(model):
    url = reverse("main:" + model.__class__.__name__.lower(), args=(model.id,))
    return mark_safe(f'<a class="model_url" href="{url}">{escape(model.name)}</a>')