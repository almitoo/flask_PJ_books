from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client.bookgrocer  # שם בסיס הנתונים
users_collection = db.users  # טבלת המשתמשים
books_collection = db.books