from django.template.defaultfilters import escape
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import template

from broker import models

register = template.Library()

@register.filter
def model(model, count=True):
    url = reverse("main:" + model.__class__.__name__.lower(), args=(model.id,))
    if count:
        if (model.__class__ == models.Type):
            variants = models.Variant.objects.filter(type=model)
            count = models.Tree.objects.filter(variant__in=variants).count()
        elif (model.__class__ == models.Variant):
            count = models.Tree.objects.filter(variant=model.id).count()
        else:
            count = 0
    return mark_safe(f'<a class="model_url" href="{url}">{escape(model.name)}{(" (%s)" % count) if count is not False else ""}</a>')