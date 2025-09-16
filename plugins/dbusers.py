import motor.motor_asyncio
from typing import Optional, List, Dict
from config import DB_NAME, DB_URI

# ---------------- Database Class ----------------
class Database:
    def __init__(self, uri: str, database_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users_col = self.db["users"]  # Collection name

    # Create a new user dictionary
    def new_user(self, user_id: int, name: str) -> Dict:
        return {"id": user_id, "name": name}

    # Add a new user to the database
    async def add_user(self, user_id: int, name: str) -> None:
        if not await self.is_user_exist(user_id):
            user = self.new_user(user_id, name)
            await self.users_col.insert_one(user)

    # Check if a user exists
    async def is_user_exist(self, user_id: int) -> bool:
        user = await self.users_col.find_one({"id": int(user_id)})
        return bool(user)

    # Count total users
    async def total_users_count(self) -> int:
        return await self.users_col.count_documents({})

    # Retrieve all users (returns async cursor)
    async def get_all_users(self):
        return self.users_col.find({})

    # Delete a specific user
    async def delete_user(self, user_id: int) -> None:
        await self.users_col.delete_many({"id": int(user_id)})

    # Get user by ID
    async def get_user(self, user_id: int) -> Optional[Dict]:
        return await self.users_col.find_one({"id": int(user_id)})

# ---------------- Initialize Database ----------------
db = Database(DB_URI, DB_NAME)