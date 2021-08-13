from django.views import generic
from django.shortcuts import render

from broker.models import Tree

import OrchardVision.settings as settings

class MapView(generic.TemplateView):
    template_name = "orchardMap/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['trees'] = Tree.objects.all()
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY

        return context

class TreeInfo(generic.TemplateView):
    template_name = "orchardMap/treeInfo.html"

    def get_context_data(self, **kwargs):
        kwargs['tree'] = Tree.objects.get(pk=kwargs['tree'])
        return super().get_context_data(**kwargs)