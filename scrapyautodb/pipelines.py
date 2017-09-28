# -*- coding: utf-8 -*-
from importlib import import_module
import datetime
from itertools import chain
import peewee
import scrapy
from scrapy.utils.project import get_project_settings


class AutoDBPipeline(object):
    def __init__(self):
        self.settings = get_project_settings()
        self._connect_db()
        project = self.settings.get("BOT_NAME")
        items = import_module('.'.join((project, "items")))
        self.l_items = [x for x in dir(items) if isinstance(getattr(items, x), scrapy.item.ItemMeta)]
        self.l_models = dict()
        for t_item in self.l_items:
            item = getattr(items, t_item)
            meta = getattr(item, 'Meta', type("Meta", (), {}))
            meta.database = self.db
            l_field_names = item.fields
            model = type(t_item, (peewee.Model,), {"Meta": meta})
            for field_name, d in l_field_names.items():
                peewee.TextField(null=True, **d).add_to_class(model, field_name)
            peewee.DateTimeField(default=datetime.datetime.now).add_to_class(model, "create_date")
            peewee.DateTimeField(default=datetime.datetime.now).add_to_class(model, "modify_date")
            self.l_models[t_item] = model
        self.db.create_tables(self.l_models.values(), safe=True)

    def _connect_db(self):
        db_settings = self.settings.get("DATABASE")
        if db_settings is None:
            raise ValueError("DATABASE is not set")
        db_params = db_settings.get("params")
        db_engine = db_settings.get("engine")
        if db_engine.lower() == "sqlite":
            self.db = peewee.SqliteDatabase(**db_params)
        elif db_engine.lower() == "mysql":
            self.db = peewee.MySQLDatabase(**db_params)
        elif db_engine.lower() == "postgresql":
            self.db = peewee.PostgresqlDatabase(**db_params)
        else:
            raise ValueError("DATABASE engine is not supported")

    def process_item(self, item, spider):
        item_name = item.__class__.__name__
        model = self.l_models[item_name]
        indexes = getattr(model._meta, "indexes")
        if indexes:
            d_constraints = {}
            constraints = set(chain(*(i[0] for i in indexes if i[1])))
            for constraint in constraints:
                d_constraints[constraint] = item.pop(constraint)
            instance, created = model.get_or_create(**d_constraints)
            model.update(modify_date=datetime.datetime.now(), **item).where(model.id == instance.id).execute()
        else:
            instance = model(**item)
            try:
                instance.save()
            except peewee.IntegrityError as e:
                print(e)
            return instance
