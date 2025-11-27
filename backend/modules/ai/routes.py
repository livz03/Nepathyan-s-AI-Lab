from fastapi import APIRouter, HTTPException
from backend.modules.ai.llm import llm_service
from backend.modules.attendance.service import get_attendance_history
from backend.database.connection import get_database

router = APIRouter(tags=["AI"])

@router.post("/chat")
async def chat(prompt: str, context: str = ""):
    response = await llm_service.generate_response(prompt, context)
    return {"response": response}

@router.get("/insights/{user_id}")
async def get_insights(user_id: str):
    try:
        # Fetch user name (mock for now, should fetch from DB)
        db = await get_database()
        user = await db.users.find_one({"_id": user_id})
        user_name = user["name"] if user else "User"
        
        history = await get_attendance_history(user_id)
        # Convert datetime objects to string for JSON serialization/prompt
        history_str = [{"timestamp": str(h["timestamp"]), "status": h.get("status", "Present")} for h in history[:10]]
        
        insight = await llm_service.analyze_attendance(history_str, user_name)
        return {"insight": insight}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
