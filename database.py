import pymongo
import sys

try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    print("Connected to MongoDB")
except Exception:
    print("Unable to connect to the mongodb server.")
    sys.exit(0)
