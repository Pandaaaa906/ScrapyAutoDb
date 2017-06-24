ScrapyAutoDb
======

Storing items to database using peewee

Features
======
Automatically update existed records and log create date and modify date.

Example
-------
        class myItem(scrapy.Item):
            name = scrapy.Field()
            phone_num = scrapy.Field()

            class Meta:
                indexes = (
                    (('name','phone_num'), True),
                )
How to use
======
	1. Install scrapyautodb.
	2. In settings.py add database settings like below:
        DATABASE = {
           "engine":"sqlite",
           "params":{
               "database":"scrapy_db.db"
            }
        }
	3. In settings.py add pipeline settings:
	    ITEM_PIPELINES = {
	    	'scrapyautodb.pipelines.AutoDBPipeline': 100,
       }

Advance
=======
Supported Multiple Database Engines:

SQLite

    DATABASE = {
       "engine":"sqlite",
       "params":{
           "database":"scrapy_db.db"
        }
    }

MySQL

    DATABASE = {
        "engine":"mysql",
        "params":{
            "database":"databasename",
            "user":"username",
            "passwd":"password",
            "host":"localhost",
            "port":3306,
        }
    }

PostgreSQL

    DATABASE = {
        "engine":"postgresql",
        "params":{
            "database":"databasename",
            "user":"username",
            "password":"password",
            "host":"localhost",
            "port":2345,
        }
    }