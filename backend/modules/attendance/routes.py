from fastapi import APIRouter, Depends
from backend.modules.attendance import service
from backend.utils.security import get_current_user

router = APIRouter(tags=["Attendance"])

@router.post("/mark")
async def mark_attendance_route(current_user = Depends(get_current_user)):
    return await service.mark_attendance(current_user["_id"])

@router.get("/history")
async def get_history_route(current_user = Depends(get_current_user)):
    return await service.get_attendance_history(current_user["_id"])

@router.get("/all")
async def get_all_attendance_route(current_user = Depends(get_current_user)):
    # In a real app, check for admin role here
    return await service.get_all_attendance()
