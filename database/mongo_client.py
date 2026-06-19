import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_client():
    return MongoClient(os.getenv("MONGODB_URI"))

def get_collection():
    client = get_client()
    db = client["requirement_tracker"]
    return db["raw_intake"]

def insert_raw_intake(data: dict) -> str:
    collection = get_collection()
    data["submitted_at"] = datetime.utcnow()
    data["processed"] = False
    result = collection.insert_one(data)
    return str(result.inserted_id)

def mark_as_processed(mongo_id: str):
    from bson import ObjectId
    collection = get_collection()
    collection.update_one(
        {"_id": ObjectId(mongo_id)},
        {"$set": {"processed": True, "processed_at": datetime.utcnow()}}
    )

def get_all_raw_intake():
    collection = get_collection()
    return list(collection.find().sort("submitted_at", -1))

def get_raw_by_id(mongo_id: str):
    from bson import ObjectId
    collection = get_collection()
    return collection.find_one({"_id": ObjectId(mongo_id)})

def get_all_titles_and_descriptions():
    collection = get_collection()
    return list(collection.find(
        {},
        {"title": 1, "description": 1, "_id": 1}
    ))