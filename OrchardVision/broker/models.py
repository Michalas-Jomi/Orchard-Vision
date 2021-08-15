from django.db import models
from django.utils import timezone


def _repr(self):
    res = {}
    
    for name, value in self.__dict__.items():
        if not name.startswith('_'):
            res[name] = str(value)
    
    return self.__class__.__name__ + str(res)
models.Model.__repr__ = _repr
models.Model.__str__ = _repr
del _repr



@classmethod
def _get(cls, **sqlParams):
    type, created = cls.objects.get_or_create(**sqlParams)

    if created:
        Actions.objects.create(type='insert ' + cls.__name__, note=str(type))

    return type


class Type(models.Model):
    name = models.TextField(unique=True)
    note = models.TextField(default='')

    get = _get

class Variant(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    name = models.TextField()
    harvest_time = models.SmallIntegerField(null=True)# I połowa lipca | II Połowa śierpnia...
    note = models.TextField(default='')

    get = _get

class Tree(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.PROTECT)
    latitude = models.FloatField()
    longitude = models.FloatField()
    planting_data = models.DateField()
    note = models.TextField(default='')

    def getLocation(self):
        return self.latitude, self.longitude


class Actions(models.Model):
    date = models.DateTimeField(default=timezone.now)
    author = models.TextField(null=True)
    type = models.TextField()
    note = models.TextField(default='')