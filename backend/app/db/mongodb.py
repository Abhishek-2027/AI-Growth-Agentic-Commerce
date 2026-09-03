from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    global _client, _database
    try:
        uri = settings.effective_mongodb_uri
        _client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=10000)
        _database = _client[settings.mongodb_database]
        # Ping to confirm connection
        await _database.command("ping")
        logger.info(f"Connected to MongoDB Atlas: database='{settings.mongodb_database}'")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_db() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _database


def get_collection(name: str):
    return get_database()[name]
