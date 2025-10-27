import os
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

MONGO_URI=os.getenv("MONGO_URI")

client=AsyncIOMotorClient(MONGO_URI,serverSelectionTimeoutMs=5000)
db=client["fastapi_auth_db"]
users_collection=db["users"]




"""
===========================================================
📘 database.py — MongoDB (Atlas) Connection Setup for FastAPI
===========================================================

1. Loads environment variables using dotenv (.env file must contain MONGO_URI).
2. Creates an asynchronous connection to MongoDB using Motor (AsyncIOMotorClient).
3. Motor is the async driver for MongoDB built on top of PyMongo.
4. The connection is non-blocking — ideal for async frameworks like FastAPI.
5. serverSelectionTimeoutMS=5000 ensures the client fails fast if the DB is unreachable.
6. Accesses or auto-creates the database named "fastapi_auth_db" inside the cluster.
7. Accesses or auto-creates the "users" collection where all user data will be stored.
8. Collections in MongoDB are schema-less — documents (records) can have flexible fields.
9. This file exports `users_collection` so it can be used in routes, auth logic, etc.
10. MongoDB Atlas manages the cloud database; no local DB installation required.

Usage Example:
--------------
from database import users_collection

await users_collection.insert_one({"email": "test@gmail.com", "password": "hashed_pw"})
===========================================================
"""
