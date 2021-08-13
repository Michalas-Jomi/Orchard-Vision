from datetime import date

from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, Http404
from django.views.decorators.csrf import csrf_exempt

from . import models

import json



def _get_from_post(request, key):
    if key in request.POST:
        return request.POST.get(key)
    raise HttpResponseBadRequest()

def _get_tree_from_post(request):
    type = _get_from_post(request, 'type')
    variant = _get_from_post(request, 'variant')
    note = request.POST.get('note', '')

    type = models.Type.get(type)
    variant = models.Variant.get(variant, type)

    return type, variant, note

def needPost(func):
    def f(request, *args, **kwargs):
        if (len(request.POST) == 0):
            raise Http404()
        return func(request, *args, **kwargs)
    return f    


class Edit:
    __slots__ = ('model', 'pre')

    def __init__(self, model):
        self.model = model
        self.pre = str(model)
    def __enter__(self):
        pass
    def __exit__(self, type, value, traceback):
        models.Actions.objects.create(type="edit " + self.model.__class__.__name__, note=self.pre + " -> " + str(self.model))


@csrf_exempt
@needPost
def insert(request : HttpRequest):
    longitude = float(_get_from_post(request, 'longitude'))
    latitude = float(_get_from_post(request, 'latitude'))
    type, variant, note = _get_tree_from_post(request)
    age = int(_get_from_post(request, 'age'))

    today = date.today()

    tree = models.Tree.objects.create(variant=variant, latitude=latitude, longitude=longitude,
            planting_data=today.replace(year = today.year - age), note=note)

    models.Actions.objects.create(type='insert Tree', note=str(tree))

    return HttpResponse()

@csrf_exempt
def initinfo(request : HttpRequest):
    _json = {}
    
    variants = {}
    _json['types'] = variants
    for variant in models.Variant.objects.all():
        type_name = variant.type.name
        if type_name not in variants:
            variants[type_name] = []
        variants[type_name].append(variant.name)

    _json['trees'] = [
        {'id': tree.id, 'latitude': tree.latitude, 'longitude': tree.longitude, 'variant': tree.variant.name, 'type': tree.variant.type.name}
            for tree in models.Tree.objects.all()
    ]

    return HttpResponse(json.dumps(_json))


@needPost
def editTree(request : HttpRequest):
    planting_date = _get_from_post(request, 'planting_data')
    type, variant, note = _get_tree_from_post(request)
    id = _get_from_post(request, 'id')

    tree = models.Tree.objects.get(pk=id)

    with Edit(tree):
        tree.variant = variant
        tree.planting_data = planting_date
        tree.note = note
        
        tree.save()

    return HttpResponse()
@needPost
def editType(request : HttpRequest):
    id = _get_from_post(request, 'id')
    name = _get_from_post(request, 'name')
    note = _get_from_post(request, 'note')

    type = models.Type.objects.get(pk=id)

    with Edit(type):
        type.name = name
        type.note = note

        type.save()

    return HttpResponse()
@needPost
def editVariant(request : HttpRequest):
    id = _get_from_post(request, 'id')
    name = _get_from_post(request, 'name')
    type = _get_from_post(request, 'type')
    note = _get_from_post(request, 'note')

    print(type)

    variant = models.Variant.objects.get(pk=id)
    type = models.Type.objects.get(pk=type)

    with Edit(variant):
        variant.name = name
        variant.type = type
        variant.note = note

        variant.save()

    return HttpResponse()

