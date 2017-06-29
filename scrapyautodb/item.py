from collections import OrderedDict
from abc import ABCMeta
import itertools

import scrapy
import six
from scrapy.item import DictItem


class Field(dict):
    _counter = itertools.count()

    def __init__(self, *args, **kwargs):
        super(Field, self).__init__(*args, **kwargs)
        self.count = Field._counter.next()


class ItemMeta(scrapy.item.ItemMeta):
    def __new__(mcs, class_name, bases, attrs):
        new_bases = tuple(base._class for base in bases if hasattr(base, '_class'))
        _class = super(ItemMeta, mcs).__new__(mcs, 'x_' + class_name, new_bases, attrs)

        tmp_fields = getattr(_class, 'fields', OrderedDict())
        new_attrs = {}
        for n in dir(_class):
            v = getattr(_class, n)
            if isinstance(v, Field):
                tmp_fields[n] = v
            elif n in attrs:
                new_attrs[n] = attrs[n]

        sorted_keys = sorted(tmp_fields, key=lambda tkey: mcs._key(_class, tkey))
        fields = OrderedDict()
        for key in sorted_keys:
            fields[key] = tmp_fields.pop(key)

        new_attrs['fields'] = fields
        new_attrs['_class'] = _class
        return super(ItemMeta, mcs).__new__(mcs, class_name, bases, new_attrs)

    def _key(cls, attr):
        field = getattr(cls, attr)
        if hasattr(field, "count"):
            return field.count
        else:
            raise AttributeError("Field Type is wrong")


@six.add_metaclass(ItemMeta)
class OrderedItem(DictItem):
    pass
