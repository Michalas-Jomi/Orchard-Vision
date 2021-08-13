from django.views.generic import ListView, DetailView

from broker import models

class IndexView(ListView):
    template_name = "main/index.html"
    context_object_name = 'variants'
    model = models.Variant
    ordering = 'type_id'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        types = set()
        for variant in kwargs['variants']:
            types.add(variant.type_id)
        kwargs['empty_types'] = models.Type.objects.exclude(id__in=types)

        return kwargs


class TypeView(DetailView):
    template_name = "main/type.html"
    context_object_name = "type"
    model = models.Type

    def get_context_data(self, **kwargs):
        kwargs =  super().get_context_data(**kwargs)

        type = kwargs[self.context_object_name]
        variants = models.Variant.objects.filter(type=type)
        trees = models.Tree.objects.filter(variant__in=variants)

        kwargs['trees'] = trees.count()

        return kwargs
class TypeEditView(DetailView):
    template_name = "main/typeEdit.html"
    context_object_name = "type"
    model = models.Type
    

class VariantView(DetailView):
    template_name = "main/variant.html"
    context_object_name = "variant"
    model = models.Variant

    def get_context_data(self, **kwargs):
        kwargs =  super().get_context_data(**kwargs)

        variant = kwargs[self.context_object_name]
        kwargs['trees'] = models.Tree.objects.filter(variant=variant).count()

        return kwargs
class VariantEditView(DetailView):
    template_name = "main/variantEdit.html"
    context_object_name = "variant"
    model = models.Variant

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res.update({'types': models.Type.objects.all()})
        return res

