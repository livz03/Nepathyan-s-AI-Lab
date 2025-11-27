from fastapi import APIRouter, HTTPException, Depends
from backend.database.connection import get_database
from backend.utils.security import get_current_user
from datetime import datetime
import pytz

router = APIRouter(tags=["Attendance"])

NEPAL_TZ = pytz.timezone('Asia/Kathmandu')

@router.post("/check-in")
async def check_in(current_user = Depends(get_current_user)):
    db = await get_database()
    user_id = current_user["_id"]
    
    # Check if already checked in today
    today_start = datetime.now(NEPAL_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    existing = await db.attendance.find_one({
        "user_id": user_id,
        "date": today_start.date().isoformat(),
        "check_out": None
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in")
    
    record = {
        "user_id": user_id,
        "user_name": current_user.get("name"),
        "date": datetime.now(NEPAL_TZ).date().isoformat(),
        "check_in": datetime.now(NEPAL_TZ).isoformat(),
        "check_out": None,
        "status": "present",
        "timestamp": datetime.now(NEPAL_TZ)
    }
    
    await db.attendance.insert_one(record)
    return {"message": "Checked in successfully", "time": record["check_in"]}

@router.post("/check-out")
async def check_out(current_user = Depends(get_current_user)):
    db = await get_database()
    user_id = current_user["_id"]
    
    # Find today's check-in
    today_start = datetime.now(NEPAL_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    record = await db.attendance.find_one({
        "user_id": user_id,
        "date": today_start.date().isoformat(),
        "check_out": None
    })
    
    if not record:
        raise HTTPException(status_code=400, detail="No active check-in found")
    
    check_out_time = datetime.now(NEPAL_TZ).isoformat()
    await db.attendance.update_one(
        {"_id": record["_id"]},
        {"$set": {"check_out": check_out_time}}
    )
    
    return {"message": "Checked out successfully", "time": check_out_time}

@router.get("/my-history")
async def get_my_history(current_user = Depends(get_current_user)):
    db = await get_database()
    history = await db.attendance.find(
        {"user_id": current_user["_id"]}
    ).sort("timestamp", -1).to_list(length=100)
    
    return history

@router.get("/status")
async def get_attendance_status(current_user = Depends(get_current_user)):
    db = await get_database()
    today_start = datetime.now(NEPAL_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    
    record = await db.attendance.find_one({
        "user_id": current_user["_id"],
        "date": today_start.date().isoformat()
    })
    
    if not record:
        return {"status": "not_checked_in", "checked_in": False}
    
    return {
        "status": "checked_in" if not record.get("check_out") else "checked_out",
        "checked_in": True,
        "check_in_time": record.get("check_in"),
        "check_out_time": record.get("check_out")
    }
