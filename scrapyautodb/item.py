from collections import OrderedDict
from abc import ABCMeta
import itertools
import six
from scrapy.item import DictItem


class Field(dict):
    _counter = itertools.count()

    def __init__(self, *args, **kwargs):
        super(Field, self).__init__(*args, **kwargs)
        self.count = Field._counter.next()


class ItemMeta(ABCMeta):
    def __new__(mcs, class_name, bases, attrs):
        new_bases = tuple(base._class for base in bases if hasattr(base, '_class'))
        _class = super(ItemMeta, mcs).__new__(mcs, 'x_' + class_name, new_bases, attrs)

        fields = getattr(_class, 'fields', {})
        new_attrs = {}
        for n in dir(_class):
            v = getattr(_class, n)
            if isinstance(v, Field):
                fields[n] = v
            elif n in attrs:
                new_attrs[n] = attrs[n]

        fields = OrderedDict(sorted(fields.items(), key=lambda item: getattr(_class, item[0]).count))

        new_attrs['fields'] = fields
        new_attrs['_class'] = _class
        return super(ItemMeta, mcs).__new__(mcs, class_name, bases, new_attrs)


@six.add_metaclass(ItemMeta)
class OrderedItem(DictItem):
    pass
