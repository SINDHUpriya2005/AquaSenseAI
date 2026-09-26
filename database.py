"""
MongoDB connection management using Motor (async driver).

The client is created once at app startup and reused across requests.
Collections are exposed as simple properties so routers can do:
    from app.db.database import db
    await db.users.find_one(...)
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


class Database:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    @property
    def users(self):
        return self.db["users"]

    @property
    def purifiers(self):
        return self.db["purifiers"]

    @property
    def readings(self):
        return self.db["readings"]

    @property
    def predictions(self):
        return self.db["predictions"]

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB_NAME]
        await self._ensure_indexes()

    async def disconnect(self):
        if self.client:
            self.client.close()

    async def _ensure_indexes(self):
        await self.users.create_index("email", unique=True)
        await self.purifiers.create_index("owner_id")
        await self.readings.create_index([("purifier_id", 1), ("recorded_at", -1)])
        await self.predictions.create_index([("purifier_id", 1), ("created_at", -1)])


db = Database()
