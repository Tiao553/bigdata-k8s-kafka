# import libraries
import os
import pandas as pd
from dotenv import load_dotenv
from data_requests.api_requests import Requests
from pymongo import MongoClient
#from objects.payments import Payments

# get env
load_dotenv()

# load variables
mongodb = os.getenv("MONGODB")
mongodb_database = os.getenv("MONGODB_DATABASE")

client = MongoClient(mongodb)
db = client[mongodb_database]

print(db.list_collection_names())