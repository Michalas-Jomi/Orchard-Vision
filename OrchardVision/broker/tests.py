from datetime import date, timedelta
from django.http import response
from django.test import TestCase
from django.urls import reverse
from django.utils import tree

from . import models, views

import random
import json


ALPHABET = 'aAąĄbBcCćĆdDeEęĘfFgGhHiIjJkKlLmMnNńŃoOóÓpPrRsStTuUwWxXyYzZźŹżŻ'
NUMS = '0123456789'
SPECIAL_CHARACTERS = '(){}[]<>!@#$%^&?/*+-=\'",.\\/'


def generate_LatLng() -> tuple:
    return (random.random() * 100, random.random() * 100)
def generate_Text(min_len=30, max_len=100, alphabet=None, **kwargs) -> str:
    if alphabet is None:
        alphabet = ALPHABET + NUMS + SPECIAL_CHARACTERS
    le = random.randint(min_len, max_len)

    res = ''
    while (len(res) < le):
        res += random.choice(alphabet)
    
    return res
def generate_date() -> date:
    return date(year=1970, month=1, day=1) + timedelta(days=random.randint(1, 365) * random.randrange(200))
    return date(year=1970) + timedelta(days=random.randrange(28), months=random.randrange(12), years=random.randrange(200))
def generateTreeKwargs(**kwargs) -> dict:
    latitude, longitude = generate_LatLng()
    return {'type' : generate_Text(**kwargs), 'variant': generate_Text(**kwargs), 'age' : random.randrange(200),
            'latitude' : latitude, 'longitude' : longitude, 'note' : generate_Text(**kwargs)}
def generateTree(**kwargs) -> models.Tree:
    treeKwargs = generateTreeKwargs(**kwargs)

    treeKwargs['planting_data'] = date.today().replace(year = date.today().year - treeKwargs.pop('age'))

    del treeKwargs['type']
    if 'variant' not in kwargs or not isinstance(kwargs['variant'], models.Variant):
        type, _ = models.Type.objects.get_or_create(name=generate_Text(**kwargs))
        variant, _ = models.Variant.objects.get_or_create(name=generate_Text(**kwargs), type=type)
        treeKwargs['variant'] = variant
    else:
        treeKwargs['variant'] = kwargs['variant']

    return models.Tree.objects.create(**treeKwargs)

def generateNameNote() -> dict:
    return {'name': generate_Text(), 'note': generate_Text()}

def generateType() -> models.Type:
    return models.Type.objects.create(**generateNameNote())
def generateVariant(type) -> models.Variant:
    return models.Variant.objects.create(type=type, **generateNameNote())


def assertTree(self, tree, treeKwargs):
    def test(key, getter):
        if key in treeKwargs:
            self.assertEqual(getter(), treeKwargs[key])
    test('type',          lambda: tree.variant.type.name)
    test('variant',       lambda: tree.variant.name)
    test('age',           lambda: date.today().year - tree.planting_data.year)
    test('planting_data', lambda: tree.planting_data)
    test('latitude',      lambda: tree.latitude)
    test('longitude',     lambda: tree.longitude)
    test('note',          lambda: tree.note)


def assertRequestCode(self, url, data={}, code=200) -> response.HttpResponse:
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, code)
    return response



class ModelsTests(TestCase):
    def test_Tree_method_getLocation(self):
        latitude, longitude = generate_LatLng()

        tree = models.Tree(latitude=latitude, longitude=longitude, planting_data=date.today())
        self.assertTrue(tree.getLocation() == (latitude, longitude))

class viewsUtilsTests(TestCase):
    def test_prepare_date(self):
        for InalidDate in '11-22-33', '111-22-33', '11-222-333', '11-2222-33', '1111-2222-33', '1111-22-3333':
            self.assertRaises(response.Http404, lambda: views._prepare_date(InalidDate))
        self.assertEqual(views._prepare_date('11-22-3333'), '3333-22-11')
        self.assertEqual(views._prepare_date('1111-22-33'), '1111-22-33')
    def test_get_from_post(self):
        self.POST = {}
        self.assertRaises(response.Http404, lambda: views._get_from_post(self, 'key'))

        self.POST = {'antoherkey': 'some value'}
        self.assertRaises(response.Http404, lambda: views._get_from_post(self, 'key'))

        self.POST = {'key': 'some value'}
        self.assertEqual(views._get_from_post(self, 'key'), 'some value')
    def test_get_tree_from_post(self):
        self.POST = {
            'type': generate_Text(),
            'variant': generate_Text(),
            'note': generate_Text(),
        }

        type, variant, note = views._get_tree_from_post(self)

        self.assertEqual(type.name, self.POST['type'])
        self.assertEqual(variant.name, self.POST['variant'])
        self.assertEqual(note, self.POST['note'])

        views._get_tree_from_post(self)
        views._get_tree_from_post(self)

        self.POST['variant'] = generate_Text()

        views._get_tree_from_post(self)

        self.assertEqual(models.Type.objects.count(), 1)
        self.assertEqual(models.Variant.objects.count(), 2)
        
    def test_need_post(self):
        @views.needPost
        def postFunc(request, arg1):
            return arg1 + 2
        
        self.POST = {'1': 2}
        self.assertEqual(postFunc(self, 3), 5)

        self.assertRaises(TypeError, lambda: postFunc(self))

        self.POST = {}
        self.assertRaises(response.Http404, lambda: postFunc(self, 3))

        

class UniversalViewsTests(TestCase):
    def test_initInfo(self):
        trees = [generateTree(min_len=1, max_len=2, alphabet='abc') for i in range(100)]

        response = assertRequestCode(self, reverse('broker:initinfo'))

        _json = response.content.decode('utf-8')
        _json = json.loads(_json)

        self.assertEqual(len(_json['types']), models.Type.objects.count())
        self.assertEqual(sum(map(lambda x: len(x), _json['types'].values())), models.Variant.objects.count())
        self.assertEqual(len(_json['trees']), len(trees))
        self.assertEqual(len(trees), models.Tree.objects.count())

        def toTree(json):
            type = models.Type.objects.get(name=json.pop('type'))
            variant = models.Variant.objects.get(name=json.pop('variant'), type=type)
            tree = models.Tree(variant=variant, **json)
            return tree
        
        jsonTrees = [toTree(json) for json in _json['trees']]

        for dbtree in trees:
            was = False
            for i in range(len(jsonTrees)):
                tree = jsonTrees[i]
                if tree == dbtree:
                    was = True
                    del jsonTrees[i]
                    break
            if not was:
                self.fail()
        self.assertEqual(len(jsonTrees), 0)

class EditViewsTests(TestCase):
    def test_editType(self):
        type = generateType()

        data = dict(
            generateNameNote(),
            id = type.id,
        )

        assertRequestCode(self, reverse('broker:editType'), data)

        type = models.Type.objects.get(pk=type.id)

        self.assertEqual(type.name, data['name'])
        self.assertEqual(type.note, data['note'])

    def test_editVariant(self):
        type1 = generateType()
        type2 = generateType()
        variant = generateVariant(type=type1)

        data = dict(
            **generateNameNote(),
            id = variant.id,
            type = type2.id,
        )

        assertRequestCode(self, reverse('broker:editVariant'), data)

        variant = models.Variant.objects.get(pk=variant.id)

        self.assertEqual(variant.name, data['name'])
        self.assertEqual(variant.note, data['note'])
        self.assertEqual(variant.type, type2)
        
    def test_editTree(self):
        newTreeKwargs = generateTreeKwargs()

        newTreeKwargs['planting_data'] = date.today().replace(year = date.today().year - newTreeKwargs.pop('age'))

        del newTreeKwargs['latitude']
        del newTreeKwargs['longitude']

        tree = generateTree()
        newTreeKwargs['id'] = tree.id

        assertRequestCode(self, reverse('broker:editTree'), newTreeKwargs)

        tree = models.Tree.objects.get(pk=tree.id)

        assertTree(self, tree, newTreeKwargs)
        
    def test_editTreeMove(self):
        tree = generateTree()

        data = {
            'id': tree.id,
            'lat': random.random(),
            'lng': random.random(),
        }

        assertRequestCode(self, reverse('broker:editTreeMove'), data)

        tree = models.Tree.objects.get(pk=tree.id)

        self.assertEqual(data['lat'], tree.latitude)
        self.assertEqual(data['lng'], tree.longitude)
    
    def test_editHarvestTime(self):
        harvest = models.HarvestTime.objects.create(title=generate_Text(), start=generate_date(), end=generate_date())

        title = generate_Text()
        start = generate_date()
        end   = generate_date()

        assertRequestCode(self, reverse('broker:editHarvestTime'), {'id': harvest.id, 'title': title, 'start': start, 'end': end})

        edited = models.HarvestTime.objects.get(pk=harvest.id)

        self.assertEqual(edited.title, title)
        self.assertEqual(edited.start, start.replace(year=2000))
        self.assertEqual(edited.end,   end.replace(year=2000))



class DeleteViewsTests(TestCase):
    def send(self, id, url, res):
        response = assertRequestCode(self, reverse(url, args=(id,)))
        self.assertEqual(response.content.decode('utf-8'), res)


    def test_deleteType(self):
        type = generateType()
        variant = generateVariant(type)

        self.send(type.id,      'broker:deleteType', '0')
        variant.delete()
        self.send(type.id,      'broker:deleteType', '1')
        self.send(type.id,      'broker:deleteType', '0')
        self.send(type.id + 10, 'broker:deleteType', '0')

    def test_deleteVariant(self):
        type = generateType()
        variant = generateVariant(type)
        tree = generateTree(variant=variant)

        self.send(variant.id + 10, 'broker:deleteVariant', '0')
        self.send(variant.id,      'broker:deleteVariant', '0')
        tree.delete()
        self.send(variant.id,      'broker:deleteVariant', '1')
        self.send(variant.id,      'broker:deleteVariant', '0')
    
    def test_deleteTree(self):
        tree = generateTree()

        self.assertEqual(models.Tree.objects.filter(pk=tree.id).count(), 1)

        self.send(0,           'broker:deleteTree', '0')
        self.send(tree.id,     'broker:deleteTree', '1')
        self.send(tree.id,     'broker:deleteTree', '0')
        self.send(tree.id + 1, 'broker:deleteTree', '0')
        
        self.assertEqual(models.Tree.objects.filter(pk=tree.id).count(), 0)
    
    def test_deleteHarvestTime(self):
        harvestTime = models.HarvestTime.objects.create(title=generate_Text(), start=date.today(), end=date.today())

        self.assertEqual(models.HarvestTime.objects.filter(pk=harvestTime.id).count(), 1)

        self.send(0,                  'broker:deleteHarvestTime', '0')
        self.send(harvestTime.id,     'broker:deleteHarvestTime', '1')
        self.send(harvestTime.id,     'broker:deleteHarvestTime', '0')
        self.send(harvestTime.id + 1, 'broker:deleteHarvestTime', '0')
        
        self.assertEqual(models.HarvestTime.objects.filter(pk=harvestTime.id).count(), 0)


class NewViewsTests(TestCase):
    def test_newType(self):
        data = generateNameNote()

        for code in 200, 404:
            assertRequestCode(self, reverse('broker:newType'), data, code)

        type = models.Type.objects.get(name=data['name'])
        self.assertEqual(type.name, data['name'])
        self.assertEqual(type.note, data['note'])
    
    def test_newVariant(self):
        type = generateType()
        data = dict(generateNameNote(), type=type.id)

        assertRequestCode(self, reverse('broker:newVariant'), data)

        variant = models.Variant.objects.last()

        self.assertEqual(variant.name, data['name'])
        self.assertEqual(variant.note, data['note'])
        self.assertEqual(variant.type, type)

    def test_newTree(self):
        treeKwargs = generateTreeKwargs()
        curTrees = models.Tree.objects.count()
        send = lambda: self.client.post(reverse('broker:newTree'), treeKwargs)

        self.assertEqual(send().status_code, 200)

        tree = models.Tree.objects.last()

        assertTree(self, tree, treeKwargs)

        send()

        self.assertEqual(models.Tree.objects.count(), curTrees + 2)
        type = models.Type.objects.get(name=treeKwargs['type'])
        self.assertEqual(models.Variant.objects.filter(type=type, name=treeKwargs['variant']).count(), 1)
    
    def test_newHarvestTime(self):
        title = generate_Text()
        start = generate_date()
        end   = generate_date()

        assertRequestCode(self, reverse('broker:newHarvestTime'), {'title': title, 'start': start, 'end': end})

        last = models.HarvestTime.objects.last()

        self.assertEqual(last.title, title)
        self.assertEqual(str(last.start)[4:], views._prepare_date(str(start))[4:])
        self.assertEqual(str(last.end)[4:],   views._prepare_date(str(end))[4:])
        self.assertEqual(str(last.start)[:4], '2000')

    
        


