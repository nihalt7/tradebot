import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient
from backend.app.core.config import settings

logger = logging.getLogger("TradePulseAI.DB")

# Lightweight In-Memory / Local fallback collection for when MONGODB_URI is not yet configured
class FallbackMongoCollection:
    def __init__(self, name: str):
        self.name = name
        self._docs: List[Dict[str, Any]] = []
        self._auto_id = 1

    def find_one(self, query: Dict[str, Any] = None, sort=None) -> Optional[Dict[str, Any]]:
        results = self.find(query, sort=sort)
        return results[0] if results else None

    def find(self, query: Dict[str, Any] = None, sort=None, limit: int = 0) -> List[Dict[str, Any]]:
        query = query or {}
        matched = []
        for doc in self._docs:
            match = True
            for k, v in query.items():
                if k == "$or" and isinstance(v, list):
                    or_matched = any(
                        all(doc.get(sub_k) == sub_v for sub_k, sub_v in condition.items())
                        for condition in v
                    )
                    if not or_matched:
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                matched.append(doc.copy())

        if sort:
            for field, direction in reversed(sort):
                matched.sort(key=lambda x: x.get(field, 0), reverse=(direction == -1))

        if limit > 0:
            matched = matched[:limit]
        return matched

    def insert_one(self, doc: Dict[str, Any]):
        doc_copy = doc.copy()
        if "id" not in doc_copy:
            doc_copy["id"] = self._auto_id
            self._auto_id += 1
        if "_id" not in doc_copy:
            doc_copy["_id"] = str(doc_copy["id"])
        self._docs.append(doc_copy)
        class InsertResult:
            inserted_id = doc_copy["_id"]
        return InsertResult()

    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]):
        doc = self.find_one(query)
        if doc:
            for idx, existing in enumerate(self._docs):
                if existing.get("id") == doc.get("id"):
                    if "$set" in update:
                        self._docs[idx].update(update["$set"])
                    if "$inc" in update:
                        for k, v in update["$inc"].items():
                            self._docs[idx][k] = self._docs[idx].get(k, 0) + v
                    break

    def delete_one(self, query: Dict[str, Any]):
        doc = self.find_one(query)
        if doc:
            self._docs = [d for d in self._docs if d.get("id") != doc.get("id")]

    def delete_many(self, query: Dict[str, Any] = None):
        if not query:
            self._docs.clear()
        else:
            to_remove = set(d["id"] for d in self.find(query))
            self._docs = [d for d in self._docs if d.get("id") not in to_remove]

    def count_documents(self, query: Dict[str, Any] = None) -> int:
        return len(self.find(query))

class FallbackMongoDatabase:
    def __init__(self):
        self._collections: Dict[str, FallbackMongoCollection] = {}

    def __getitem__(self, name: str) -> FallbackMongoCollection:
        if name not in self._collections:
            self._collections[name] = FallbackMongoCollection(name)
        return self._collections[name]

    def __getattr__(self, name: str) -> FallbackMongoCollection:
        return self[name]


class MongoManager:
    client: Optional[MongoClient] = None
    db: Any = None
    is_atlas: bool = False

    @classmethod
    def initialize(cls):
        uri = settings.MONGODB_URI.strip()
        if uri:
            try:
                logger.info(f"Connecting to MongoDB Atlas at {uri.split('@')[-1] if '@' in uri else 'configured URI'}...")
                cls.client = MongoClient(uri, serverSelectionTimeoutMS=4000)
                # Quick ping to test connectivity
                cls.client.admin.command('ping')
                cls.db = cls.client[settings.DATABASE_NAME]
                cls.is_atlas = True
                logger.info(f"Successfully connected to MongoDB Atlas! Database: '{settings.DATABASE_NAME}'")
                return
            except Exception as e:
                logger.warning(f"Could not connect to MongoDB Atlas ({e}). Initializing fallback in-memory store.")
        
        logger.info("Initializing high-speed PyMongo-compatible store.")
        cls.db = FallbackMongoDatabase()
        cls.is_atlas = False

def get_database():
    if MongoManager.db is None:
        MongoManager.initialize()
    return MongoManager.db

def get_db():
    return get_database()
