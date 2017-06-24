ScrapyAutoDb
============
Storing Scrapy items in database

Installation
============
    pip install git+https://github.com/Pandaaaa906/ScrapyAutoDb.git

How to use
======
	1. In settings.py add database settings like below:
        DATABASE = {
           "engine":"sqlite",
           "params":{
               "database":"scrapy_db.db"
            }
        }
	2. In settings.py add pipeline settings:
	    ITEM_PIPELINES = {
	    	'scrapyautodb.pipelines.AutoDBPipeline': 100,
       }
Features
======
Automatically update existed records and log create date and modify date.

Example
-------
        class myItem(scrapy.Item):
            name = scrapy.Field()
            phone_num = scrapy.Field()
            email = scrapy.Field()

            class Meta:
                indexes = (
                    (('name','phone_num'), True),
                )
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