import mongoengine
from mongoengine import connect
from sample_config import Config
from telemongo import MongoSession

MONGO_DB = "UserbotSession"
MONGO_URI = Config.MONGO_DB_URI
mongoengine.connect(MONGO_DB, host=MONGO_URI)
session = MongoSession(MONGO_DB, host=MONGO_URI)
