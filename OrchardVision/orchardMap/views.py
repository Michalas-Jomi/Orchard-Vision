from django.views import generic

import OrchardVision.settings as settings
from broker.models import Tree

from html import escape
import json

class MapView(generic.TemplateView):
    template_name = "orchardMap/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['trees'] = Tree.objects.all()
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY

        filter = {}
        type_filters = []

        for key, value in self.request.GET.items():
            if key.startswith('filter_'):
                type = escape(key[7:])
                if type not in filter:
                    filter[type] = {}
                filter[type][escape(value)] = True
            elif key.startswith('type_filter_'):
                type_filters.append(escape(key[12:]))
        
        context['filter'] = json.dumps(filter)
        context['type_filters'] = json.dumps(type_filters)

        return context

class TreeInfo(generic.TemplateView):
    template_name = "orchardMap/treeInfo.html"

    def get_context_data(self, **kwargs):
        kwargs['tree'] = Tree.objects.get(pk=kwargs['tree'])
        return super().get_context_data(**kwargs)