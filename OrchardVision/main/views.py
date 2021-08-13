from abc import abstractmethod
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView

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



class TypeEditView(DetailView):
    template_name = "main/typeEdit.html"
    context_object_name = "type"
    model = models.Type
class TypeView(TypeEditView):
    template_name = "main/type.html"

    def get_context_data(self, **kwargs):
        kwargs =  super().get_context_data(**kwargs)

        type = kwargs[self.context_object_name]
        variants = models.Variant.objects.filter(type=type)
        trees = models.Tree.objects.filter(variant__in=variants)

        kwargs['trees'] = trees.count()

        return kwargs
    

class abstractVariantView(DetailView):
    context_object_name = "variant"
    model = models.Variant

    def get_context_data(self, **kwargs):
        kwargs =  super().get_context_data(**kwargs)
        kwargs.update(self.getTrees(**kwargs))
        return kwargs
    @abstractmethod
    def getTrees(self, **kwargs):
        pass
class VariantView(abstractVariantView):
    template_name = "main/variant.html"

    def getTrees(self, **kwargs):
        variant = kwargs[self.context_object_name]
        return {'trees': models.Tree.objects.filter(variant=variant).count()}
class VariantEditView(abstractVariantView):
    template_name = "main/variantEdit.html"

    def getTrees(self, **kwargs):
        return {'types': models.Type.objects.all()}


class TypeNewView(TemplateView):
    template_name = "main/typeNew.html"
class VariantNewView(ListView):
    template_name = "main/variantNew.html"
    context_object_name = "types"
    model = models.Type