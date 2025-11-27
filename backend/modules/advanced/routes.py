from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from backend.database.connection import get_database
from backend.utils.security import get_current_user
from datetime import datetime, timedelta
import pytz
from typing import List, Dict

router = APIRouter(tags=["Advanced Features"])

NEPAL_TZ = pytz.timezone('Asia/Kathmandu')

def get_nepal_time():
    """Get current time in Nepal timezone"""
    return datetime.now(NEPAL_TZ)

def get_nepal_date():
    """Get current date in Nepal timezone"""
    return get_nepal_time().date()

@router.get("/lab/status")
async def get_lab_status():
    """Get current lab status based on Nepal time (12:00 PM - 5:00 PM)"""
    hour = get_nepal_time().hour
    is_open = 12 <= hour < 17
    
    return {
        "status": "OPEN" if is_open else "CLOSED",
        "current_time": get_nepal_time().strftime("%I:%M %p %Z"),
        "open_hours": "12:00 PM - 5:00 PM",
        "is_open": is_open
    }

@router.get("/lab/schedule")
async def get_lab_schedule():
    """Get weekly lab schedule"""
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    schedule = {}
    
    for day in days:
        schedule[day] = {
            "status": "OPEN",
            "hours": "12:00 PM - 5:00 PM",
            "timezone": "Asia/Kathmandu (GMT+5:45)"
        }
    
    return schedule

@router.post("/attendance/mark-absent")
async def mark_absent_for_no_shows(current_user = Depends(get_current_user)):
    """Mark absent for members who didn't check in today (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        today = get_nepal_date().isoformat()
        db = await get_database()
        
        # Get all members
        members = await db.users.find({"role": "member"}).to_list(length=100)
        
        marked_absent = []
        for member in members:
            # Check if member has attendance today
            existing = await db.attendance.find_one({
                "user_id": member["_id"],
                "date": today
            })
            
            if not existing:
                # Mark absent
                await db.attendance.insert_one({
                    "user_id": member["_id"],
                    "user_name": member.get("name", f"User_{member['_id']}"),
                    "date": today,
                    "check_in": None,
                    "check_out": None,
                    "status": "Absent",
                    "source": "auto",
                    "timestamp": get_nepal_time()
                })
                marked_absent.append(member.get("name", member["_id"]))
        
        return {
            "message": f"Marked {len(marked_absent)} members absent",
            "members": marked_absent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/member/{user_id}/stats")
async def get_member_detailed_stats(user_id: str, current_user = Depends(get_current_user)):
    """Get detailed member statistics"""
    if current_user.get("role") != "admin" and current_user.get("_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        db = await get_database()
        
        # Get all attendance records
        records = await db.attendance.find({"user_id": user_id}).to_list(length=1000)
        
        if not records:
            return {
                "total_days": 0,
                "present_days": 0,
                "absent_days": 0,
                "attendance_percentage": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "average_check_in_time": None
            }
        
        # Calculate stats
        total = len(records)
        present = len([r for r in records if r.get("status") == "Present"])
        absent = len([r for r in records if r.get("status") == "Absent"])
        percentage = (present / total * 100) if total > 0 else 0
        
        # Calculate streak
        sorted_records = sorted(records, key=lambda x: x.get("date", ""), reverse=True)
        current_streak = 0
        today = get_nepal_date()
        
        for record in sorted_records:
            if record.get("status") == "Present":
                record_date = record.get("date")
                if isinstance(record_date, str):
                    from datetime import date as dt_date
                    record_date = dt_date.fromisoformat(record_date)
                
                if (today - record_date).days == current_streak:
                    current_streak += 1
                else:
                    break
        
        return {
            "total_days": total,
            "present_days": present,
            "absent_days": absent,
            "attendance_percentage": round(percentage, 2),
            "current_streak": current_streak,
            "longest_streak": current_streak,  # Simplified
            "recent_records": sorted_records[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resources")
async def get_lab_resources(current_user = Depends(get_current_user)):
    """Get available lab resources"""
    db = await get_database()
    
    # Initialize resources if not exists
    existing = await db.resources.find_one({})
    if not existing:
        default_resources = [
            {"name": "3D Printer", "status": "available", "current_user": None},
            {"name": "High-Spec AI PC", "status": "available", "current_user": None},
            {"name": "Arduino Kit", "status": "available", "current_user": None},
            {"name": "Raspberry Pi", "status": "available", "current_user": None},
            {"name": "VR Headset", "status": "available", "current_user": None}
        ]
        await db.resources.insert_many(default_resources)
    
    resources = await db.resources.find({}).to_list(length=100)
    return resources

@router.post("/resources/{resource_id}/checkout")
async def checkout_resource(resource_id: str, current_user = Depends(get_current_user)):
    """Check out a lab resource"""
    db = await get_database()
    
    resource = await db.resources.find_one({"_id": resource_id})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if resource.get("status") != "available":
        raise HTTPException(status_code=400, detail="Resource not available")
    
    await db.resources.update_one(
        {"_id": resource_id},
        {"$set": {
            "status": "in_use",
            "current_user": current_user.get("name", current_user.get("_id")),
            "checked_out_at": get_nepal_time()
        }}
    )
    
    return {"message": "Resource checked out successfully"}

@router.post("/resources/{resource_id}/return")
async def return_resource(resource_id: str, current_user = Depends(get_current_user)):
    """Return a lab resource"""
    db = await get_database()
    
    resource = await db.resources.find_one({"_id": resource_id})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if resource.get("current_user") != current_user.get("name", current_user.get("_id")):
        raise HTTPException(status_code=403, detail="You didn't check out this resource")
    
    await db.resources.update_one(
        {"_id": resource_id},
        {"$set": {
            "status": "available",
            "current_user": None,
            "returned_at": get_nepal_time()
        }}
    )
    
    return {"message": "Resource returned successfully"}

@router.get("/reports/weekly")
async def get_weekly_report(current_user = Depends(get_current_user)):
    """Get weekly attendance report"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    today = get_nepal_date()
    week_start = (today - timedelta(days=today.weekday())).isoformat()
    
    records = await db.attendance.find({
        "date": {"$gte": week_start}
    }).to_list(length=1000)
    
    # Group by date
    daily_stats = {}
    for record in records:
        date = record.get("date")
        if date not in daily_stats:
            daily_stats[date] = {"present": 0, "absent": 0, "total": 0}
        
        daily_stats[date]["total"] += 1
        if record.get("status") == "Present":
            daily_stats[date]["present"] += 1
        else:
            daily_stats[date]["absent"] += 1
    
    return {
        "week_start": week_start,
        "daily_stats": daily_stats,
        "total_records": len(records)
    }

@router.get("/reports/monthly")
async def get_monthly_report(current_user = Depends(get_current_user)):
    """Get monthly attendance report"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    today = get_nepal_date()
    month_start = today.replace(day=1).isoformat()
    
    records = await db.attendance.find({
        "date": {"$gte": month_start}
    }).to_list(length=10000)
    
    # Calculate monthly stats
    total_present = len([r for r in records if r.get("status") == "Present"])
    total_absent = len([r for r in records if r.get("status") == "Absent"])
    
    # Get unique members
    unique_members = set(r.get("user_id") for r in records)
    
    return {
        "month_start": month_start,
        "total_records": len(records),
        "total_present": total_present,
        "total_absent": total_absent,
        "unique_members": len(unique_members),
        "attendance_rate": round((total_present / len(records) * 100), 2) if records else 0
    }
