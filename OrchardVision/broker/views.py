from datetime import date

from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpRequest, Http404
from django.views.decorators.csrf import csrf_exempt

from . import models

import json



def _get_from_post(request, key):
    if key in request.POST:
        return request.POST.get(key)
    raise Http404()

def _get_tree_from_post(request):
    type = _get_from_post(request, 'type')
    variant = _get_from_post(request, 'variant')
    note = request.POST.get('note', '')

    type = models.Type.get(name=type)
    variant = models.Variant.get(name=variant, type=type)

    return type, variant, note

def needPost(func):
    def f(request, *args, **kwargs):
        if (len(request.POST) == 0):
            raise Http404()
        return func(request, *args, **kwargs)
    return f    



### Views

## Universal

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
        {
            'id': tree.id,
            'latitude': tree.latitude,
            'longitude': tree.longitude,
            'variant': tree.variant.name,
            'type': tree.variant.type.name
        } for tree in models.Tree.objects.all()
    ]

    return HttpResponse(json.dumps(_json), content_type="application/json")


## Edit

class Edit:
    __slots__ = ('model', 'pre')

    def __init__(self, model):
        self.model = model
        self.pre = str(model)
    def __enter__(self):
        pass
    def __exit__(self, type, value, traceback):
        models.Actions.objects.create(type="edit " + self.model.__class__.__name__, note=self.pre + " -> " + str(self.model))

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
@csrf_exempt
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


## Delete

def deleteFactory(model):
    def f(request : HttpRequest, pk : int):
        try:
            model.objects.get(pk=pk).delete()
            return HttpResponse('1')
        except:
            return HttpResponse('0')
    return f

deleteType    = deleteFactory(models.Type)
deleteVariant = deleteFactory(models.Variant)
deleteTree    = deleteFactory(models.Tree)
    

## New

@needPost
def newType(request : HttpRequest):
    name = _get_from_post(request, 'name')
    note = _get_from_post(request, 'note')

    try:
        with transaction.atomic():
            models.Type.objects.create(name=name, note=note)
        return HttpResponse()
    except IntegrityError:
        raise Http404()
@needPost
def newVariant(request : HttpRequest):
    name = _get_from_post(request, 'name')
    type = _get_from_post(request, 'type')
    note = _get_from_post(request, 'note')

    try:
        type = models.Type.objects.get(pk=type)
        with transaction.atomic():
            models.Variant.objects.create(name=name, type=type, note=note)
        return HttpResponse()
    except:
        raise Http404()
@csrf_exempt
@needPost
def newTree(request : HttpRequest):
    longitude = float(_get_from_post(request, 'longitude'))
    latitude = float(_get_from_post(request, 'latitude'))
    type, variant, note = _get_tree_from_post(request)
    age = int(_get_from_post(request, 'age'))

    today = date.today()

    tree = models.Tree.objects.create(variant=variant, latitude=latitude, longitude=longitude,
            planting_data=today.replace(year = today.year - age), note=note)

    models.Actions.objects.create(type='insert Tree', note=str(tree))

    return HttpResponse(str(tree.id))

def infoTree(request : HttpRequest, pk : int):
    tree = models.Tree.objects.get(pk=pk)

    data = {
        "id": tree.id,
        "latitude": tree.latitude,
        "longitude": tree.longitude,
        "note": tree.note,
        "planting_date": tree.planting_data.strftime("%d-%m-%Y"),
        "variant": {
            "id": tree.variant.id,
            "name": tree.variant.name,
            "type": {
                "id": tree.variant.type.id,
                "name": tree.variant.type.name,
            }
        },
    }

    return HttpResponse(json.dumps(data), content_type="application/json")
