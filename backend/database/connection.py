from mongomock_motor import AsyncMongoMockClient
from backend.config import get_settings

settings = get_settings()

class Database:
    client = None
    db = None

    def connect(self):
        print("Using In-Memory Mock Database (MongoDB not found)")
        self.client = AsyncMongoMockClient()
        self.db = self.client[settings.DB_NAME]
        print("Connected to Mock MongoDB")

    def close(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

db = Database()

async def get_database():
    return db.db
