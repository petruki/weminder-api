import os
from flask_pymongo import pymongo

MONGO_URI = os.environ.get('MONGO_URI')

client = pymongo.MongoClient(MONGO_URI)
db = client.get_database()