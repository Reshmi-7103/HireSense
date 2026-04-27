from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("MONGO_URL")
print("Connecting...")

try:
    client = MongoClient(url, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Connected successfully!")
except Exception as e:
    print(f"❌ Error: {e}")