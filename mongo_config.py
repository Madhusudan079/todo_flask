from pymongo import MongoClient
import os
import certifi
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['user_auth_db']
collection = db['users']