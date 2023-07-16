# -*- coding: utf-8 -*-
from importlib import import_module
from datetime import datetime
from itertools import chain
import peewee
from scrapy.item import ItemMeta
import logging

from twisted.enterprise import adbapi


class AutoDBPipeline(object):
    def __init__(self, project, db_settings):
        # self.settings = get_project_settings()
        self.db_settings = db_settings
        self.project = project
        self.items = import_module('.'.join((project, "items")))
        self.l_items = [x for x in dir(self.items) if isinstance(getattr(self.items, x), ItemMeta)]
        self.l_models = dict()
        self.d_constraints = dict()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            project=crawler.settings.get('BOT_NAME'),
            db_settings=crawler.settings.get('DATABASE'),
        )

    def _connect_db(self):
        if self.db_settings is None:
            raise ValueError("DATABASE is not set")
        db_params = self.db_settings.get("params")
        cp_params = self.db_settings.get("cp_params", {})
        db_engine = self.db_settings.get("engine")
        if db_engine.lower() == "sqlite":
            adapter = self.db_settings.get("adapter", "sqlite3")
            self.db = peewee.SqliteDatabase(**db_params)
        elif db_engine.lower() == "mysql":
            adapter = self.db_settings.get("adapter", "pymysql")
            self.db = peewee.MySQLDatabase(**db_params)
        elif db_engine.lower() == "postgresql":
            adapter = self.db_settings.get("adapter", "psycopg2")
            self.db = peewee.PostgresqlDatabase(**db_params)
        else:
            raise ValueError("DATABASE engine is not supported")
        self.db_pool = adbapi.ConnectionPool(adapter, **db_params, **cp_params)

    def open_spider(self, spider):
        self._connect_db()
        for t_item in self.l_items:
            item = getattr(self.items, t_item)
            meta = getattr(item, 'Meta', type("Meta", (), {}))
            meta.database = self.db
            l_field_names = item.fields
            model = type(t_item, (peewee.Model,), {"Meta": meta})
            for field_name, d in l_field_names.items():
                model._meta.add_field(field_name, peewee.TextField(null=True, **d))
            model._meta.add_field("create_date", peewee.DateTimeField(default=datetime.now))
            model._meta.add_field("modify_date", peewee.DateTimeField(default=datetime.now))
            self.l_models[t_item] = model

            indexes = getattr(model._meta, "indexes")
            constraints = list(set(chain(*(i[0] for i in indexes if i[1]))))
            self.d_constraints[t_item] = constraints

        self.db.create_tables(self.l_models.values(), safe=True)

    def close_spider(self, spider):
        self.db.close()
        self.db_pool.close()

    def process_item(self, item, spider):
        self.db_pool.runInteraction(self._insert_db, item).addErrback(self.handle_error, item, spider)
        return item

    def _insert_db(self, cursor, item):
        item_name = item.__class__.__name__
        model = self.l_models[item_name]
        constraints = self.d_constraints[item_name]
        d = dict(item)
        d["modify_date"] = datetime.now()
        sql = model.insert(**d).on_conflict(conflict_target=constraints, preserve=list(d)).sql()
        cursor.execute(*sql)

    def handle_error(self, failure, item, spider):
        logging.log(logging.WARNING, f"Spider:{spider} Failure:{failure} Item:{item}")
