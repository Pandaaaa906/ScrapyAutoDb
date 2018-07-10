# -*- coding: utf-8 -*-
from importlib import import_module
import datetime
from itertools import chain
import peewee
from scrapy.item import ItemMeta
from scrapy.utils.project import get_project_settings
from scrapy import log


class AutoDBPipeline(object):
    def __init__(self):
        self.settings = get_project_settings()
        project = self.settings.get("BOT_NAME")
        self.items = import_module('.'.join((project, "items")))
        self.l_items = [x for x in dir(self.items) if isinstance(getattr(self.items, x), ItemMeta)]
        self.l_models = dict()
        self.d_constraints = dict()

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

    def open_spider(self):
        self._connect_db()
        for t_item in self.l_items:
            item = getattr(self.items, t_item)
            meta = getattr(item, 'Meta', type("Meta", (), {}))
            meta.database = self.db
            l_field_names = item.fields
            model = type(t_item, (peewee.Model,), {"Meta": meta})
            for field_name, d in l_field_names.items():
                model._meta.add_field(field_name, peewee.TextField(null=True, **d))
            model._meta.add_field("create_date", peewee.DateTimeField(default=datetime.datetime.now))
            model._meta.add_field("modify_date", peewee.DateTimeField(default=datetime.datetime.now))
            self.l_models[t_item] = model

            indexes = getattr(model._meta, "indexes")
            constraints = set(chain(*(i[0] for i in indexes if i[1])))
            self.d_constraints[t_item] = constraints

        self.db.create_tables(self.l_models.values(), safe=True)

    def close_spider(self):
        self.db.close()

    def process_item(self, item, spider):
        item_name = item.__class__.__name__
        model = self.l_models[item_name]
        constraints = self.d_constraints[item_name]
        try:
            instance = model.insert(**item).on_conflict(conflict_target=constraints, preserve=list(item)).execute()
        except peewee.IntegrityError as e:
            log.msg(e, level=log.ERROR)
        return item
