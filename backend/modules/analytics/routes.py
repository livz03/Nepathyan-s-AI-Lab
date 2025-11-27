from fastapi import APIRouter, HTTPException
from backend.modules.analytics.service import get_user_analytics

router = APIRouter(tags=["Analytics"])

@router.get("/user/{user_id}")
async def get_analytics(user_id: str):
    try:
        analytics = await get_user_analytics(user_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
