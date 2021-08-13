from django.views.generic import ListView, DetailView

from broker import models

class IndexView(ListView):
    template_name = "main/index.html"
    context_object_name = 'variants'
    model = models.Variant
    ordering = 'type_id'


class TypeView(DetailView):
    template_name = "main/type.html"
    context_object_name = "type"
    model = models.Type
    

class VariantView(DetailView):
    template_name = "main/variant.html"
    context_object_name = "variant"
    model = models.Variant
    

