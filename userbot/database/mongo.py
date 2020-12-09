from pymongo import MongoClient

from sample_config import Config

cli = MongoClient(Config.MONGO_DB_URI)
