from django.views import generic

import OrchardVision.settings as settings
import broker.models as models
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

class TreeInfo(generic.DetailView):
    template_name = "orchardMap/treeInfo.html"
    context_object_name = "tree"
    model = Tree

class TreeNew(generic.TemplateView):
    template_name = "orchardMap/treeNew.html"

    def get_context_data(self, **data):
        data = super().get_context_data(**data)

        data['types'] = models.Type.objects.all()
        data['variants'] = models.Variant.objects.all().order_by('type_id')

        return data

class Trees(generic.ListView):
    template_name = "orchardMap/treesJS.html"
    content_type = "application/javascript; charset=utf-8"
    context_object_name = "trees"
    model = Tree