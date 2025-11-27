from fastapi import APIRouter, HTTPException, Depends
from backend.database.connection import get_database
from backend.utils.security import get_current_user
from datetime import datetime
import pytz

router = APIRouter(tags=["Admin"])

NEPAL_TZ = pytz.timezone('Asia/Kathmandu')

@router.get("/stats")
async def get_admin_stats(current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    # Count users by role
    total_admins = await db.users.count_documents({"role": "admin"})
    total_members = await db.users.count_documents({"role": "member"})
    
    # Today's attendance
    today_start = datetime.now(NEPAL_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    present_today = await db.attendance.count_documents({
        "timestamp": {"$gte": today_start},
        "status": "present"
    })
    
    return {
        "total_admins": total_admins,
        "total_members": total_members,
        "present_today": present_today,
        "max_admins": 2,
        "max_members": 10
    }

@router.get("/members")
async def get_all_members(current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    members = await db.users.find({"role": "member"}).to_list(length=100)
    
    # Get attendance for each member
    for member in members:
        attendance_count = await db.attendance.count_documents({"user_id": member["_id"]})
        member["total_attendance"] = attendance_count
    
    return members

@router.get("/attendance/today")
async def get_today_attendance(current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    today_start = datetime.now(NEPAL_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    
    attendance = await db.attendance.find({
        "timestamp": {"$gte": today_start}
    }).to_list(length=100)
    
    return attendance

@router.post("/members/{user_id}/approve")
async def approve_member(user_id: str, current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    # Check member limit
    member_count = await db.users.count_documents({"role": "member", "is_active": True})
    if member_count >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 members allowed")
    
    result = await db.users.update_one(
        {"_id": user_id},
        {"$set": {"is_active": True}}
    )
    
    return {"message": "Member approved"}

@router.delete("/members/{user_id}")
async def remove_member(user_id: str, current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    await db.users.delete_one({"_id": user_id})
    
    return {"message": "Member removed"}
