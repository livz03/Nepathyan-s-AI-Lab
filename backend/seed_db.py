import asyncio
from backend.database.connection import db
from backend.utils.security import get_password_hash
from backend.config import get_settings

settings = get_settings()

async def seed_admin():
    db.connect()
    database = db.db
    
    # Create Admin User (ID: 100, PIN: 1111)
    # We use 'email' field for ID login as per auth service logic
    admin_user = {
        "_id": "100",
        "email": "100", 
        "name": "Admin User",
        "role": "admin",
        "hashed_password": get_password_hash("1111"),
        "is_active": True
    }
    
    try:
        # Check if admin exists
        existing = await database.users.find_one({"_id": "100"})
        if not existing:
            await database.users.insert_one(admin_user)
            print("Admin user created: ID=100, PIN=1111")
        else:
            # Update password just in case
            await database.users.update_one(
                {"_id": "100"},
                {"$set": {"hashed_password": get_password_hash("1111"), "email": "100"}}
            )
            print("Admin user updated: ID=100, PIN=1111")
            
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_admin())
