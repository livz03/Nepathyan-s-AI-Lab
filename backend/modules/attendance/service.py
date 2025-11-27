from backend.database.connection import get_database
from datetime import datetime

async def mark_attendance(user_id: str):
    db = await get_database()
    
    # Check if already marked for today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_record = await db.attendance.find_one({
        "user_id": user_id,
        "timestamp": {"$gte": today_start}
    })
    
    if existing_record:
        return {"message": "Attendance already marked for today", "record": existing_record}
    
    record = {
        "user_id": user_id,
        "timestamp": datetime.now(),
        "status": "Present"
    }
    
    new_record = await db.attendance.insert_one(record)
    created_record = await db.attendance.find_one({"_id": new_record.inserted_id})
    
    return created_record

async def get_attendance_history(user_id: str):
    db = await get_database()
    cursor = db.attendance.find({"user_id": user_id}).sort("timestamp", -1)
    history = await cursor.to_list(length=100)
    return history

async def get_all_attendance():
    db = await get_database()
    cursor = db.attendance.find().sort("timestamp", -1)
    history = await cursor.to_list(length=100)
    return history
