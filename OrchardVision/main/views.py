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

        kwargs['trees'] = models.Tree.objects.count()

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
    
class TypeNewView(TemplateView):
    template_name = "main/typeNew.html"



class abstractVariantView(DetailView):
    context_object_name = "variant"
    model = models.Variant

    def get_context_data(self, **kwargs):
        kwargs =  super().get_context_data(**kwargs)
        kwargs.update(self.getContext(**kwargs))
        return kwargs
    @abstractmethod
    def getContext(self, **kwargs):
        pass
class VariantView(abstractVariantView):
    template_name = "main/variant.html"

    def getContext(self, **kwargs):
        variant = kwargs[self.context_object_name]
        return {'trees': models.Tree.objects.filter(variant=variant).count()}
class VariantEditView(abstractVariantView):
    template_name = "main/variantEdit.html"
    extra_context = {
        'parent': 'main/variantNew.html',
        'deleteUrl': "broker:deleteVariant",
        'url': 'broker:editVariant',
    }
    
    def getContext(self, **kwargs):
        return {
            'model': kwargs[self.context_object_name],
            'types': models.Type.objects.all(),
            'harvest_times': models.HarvestTime.objects.all()
        }

class VariantNewView(ListView):
    template_name = "main/variantNew.html"
    context_object_name = "types"
    model = models.Type


class HarvestTimeNewView(TemplateView):
    template_name = "main/harvestTime.html"
class HarvestTimesView(ListView):
    template_name = "main/harvestTimes.html"
    context_object_name = "harvest_times"
    model = models.HarvestTime
    ordering = 'start'
    extra_context = {
        'url': 'broker:newHarvestTime',
        'header': 'Nowy czas zbiorów',
    }
class HarvestTimeEditView(DetailView):
    template_name = "main/harvestTime.html"
    context_object_name = "harvestTime"
    model = models.HarvestTime
    extra_context = {
        'url': 'broker:editHarvestTime',
        'header': 'Edycja czasu zbiorów',
    }
