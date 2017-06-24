ScrapyAutoDb
===

Export items to database using peewee

Features
===
	Automatically log create date and modify date.

How to use
===
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
    4. 

