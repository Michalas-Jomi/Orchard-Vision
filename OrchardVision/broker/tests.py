from datetime import date
from django.test import TestCase
from django.urls import reverse

from . import models

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
def generateTreeKwargs(**kwargs) -> dict:
    latitude, longitude = generate_LatLng()
    return {'type' : generate_Text(**kwargs), 'variant': generate_Text(**kwargs), 'age' : random.randrange(200),
            'latitude' : latitude, 'longitude' : longitude, 'note' : generate_Text(**kwargs)}
def generateTree(**kwargs) -> models.Tree:
    treeKwargs = generateTreeKwargs(**kwargs)

    treeKwargs['planting_data'] = date.today().replace(year = date.today().year - treeKwargs.pop('age'))

    del treeKwargs['type']
    oldType, _ = models.Type.objects.get_or_create(name=generate_Text(**kwargs))
    oldVariant, _ = models.Variant.objects.get_or_create(name=generate_Text(**kwargs), type=oldType)
    treeKwargs['variant'] = oldVariant

    return models.Tree.objects.create(**treeKwargs)

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



class ModelsTests(TestCase):
    def test_Tree_method_getLocation(self):
        latitude, longitude = generate_LatLng()

        tree = models.Tree(latitude=latitude, longitude=longitude, planting_data=date.today())
        self.assertTrue(tree.getLocation() == (latitude, longitude))
    
class ViewsTests(TestCase):
    def test_insert(self):
        treeKwargs = generateTreeKwargs()
        curTrees = models.Tree.objects.count()
        send = lambda: self.client.post(reverse('broker:insert'), treeKwargs)

        response = send() 

        self.assertEqual(response.status_code, 200)

        tree = models.Tree.objects.last()

        assertTree(self, tree, treeKwargs)

        send()

        self.assertEqual(models.Tree.objects.count(), curTrees + 2)
        type = models.Type.objects.get(name=treeKwargs['type'])
        self.assertEqual(models.Variant.objects.filter(type=type, name=treeKwargs['variant']).count(), 1)

    def test_initInfo(self):
        trees = [generateTree(min_len=1, max_len=2, alphabet='abc') for i in range(100)]

        response = self.client.get(reverse('broker:initinfo'))
        self.assertEqual(response.status_code, 200)

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

    def test_editTree(self):
        newTreeKwargs = generateTreeKwargs()

        newTreeKwargs['planting_data'] = date.today().replace(year = date.today().year - newTreeKwargs.pop('age'))

        del newTreeKwargs['latitude']
        del newTreeKwargs['longitude']

        tree = generateTree()
        newTreeKwargs['id'] = tree.id

        response = self.client.post(reverse('broker:editTree'), newTreeKwargs)
        self.assertEqual(response.status_code, 200)

        tree = models.Tree.objects.get(pk=tree.id)

        assertTree(self, tree, newTreeKwargs)



