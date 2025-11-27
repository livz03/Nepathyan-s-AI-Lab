from fastapi import APIRouter, HTTPException, Depends
from backend.database.connection import get_database
from backend.utils.security import get_current_user
from backend.modules.ai.llm_client import LLMClient
from backend.modules.ai.agents import (
    AttendanceAgent, ProgressAgent, SecurityAgent, 
    PredictionAgent, MessageAgent
)

router = APIRouter(tags=["AI Agents"])

# Initialize LLM client
llm_client = LLMClient()

@router.post("/agents/attendance/analyze")
async def analyze_attendance_with_ai(current_user = Depends(get_current_user)):
    """Get AI-powered attendance insights"""
    try:
        agent = AttendanceAgent("AttendanceAgent", llm_client)
        insights = await agent.get_attendance_insights(
            current_user.get("_id"),
            current_user.get("name", f"User_{current_user.get('_id')}")
        )
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/attendance/detect-anomaly")
async def detect_attendance_anomaly(current_user = Depends(get_current_user)):
    """Detect anomalies in attendance pattern"""
    try:
        agent = AttendanceAgent("AttendanceAgent", llm_client)
        anomaly = await agent.detect_anomaly(
            current_user.get("_id"),
            current_user.get("name", f"User_{current_user.get('_id')}")
        )
        return {
            "has_anomaly": anomaly is not None,
            "anomaly": anomaly
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/learning/recommend")
async def get_learning_recommendation(current_user = Depends(get_current_user)):
    """Get AI-powered learning path recommendation"""
    try:
        agent = ProgressAgent("ProgressAgent", llm_client)
        recommendation = await agent.analyze_and_recommend(current_user.get("_id"))
        return {"recommendation": recommendation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/security/check")
async def security_check(current_user = Depends(get_current_user)):
    """Run AI security check on attendance pattern"""
    try:
        agent = SecurityAgent("SecurityAgent", llm_client)
        result = await agent.detect_suspicious_pattern(
            current_user.get("_id"),
            current_user.get("name", f"User_{current_user.get('_id')}")
        )
        return {
            "status": result,
            "is_safe": "NORMAL" in result or "SAFE" in result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/prediction/forecast")
async def forecast_attendance(current_user = Depends(get_current_user)):
    """Get AI-powered attendance forecast"""
    try:
        agent = PredictionAgent("PredictionAgent", llm_client)
        prediction = await agent.predict_attendance_rate(current_user.get("_id"))
        return {
            "predicted_rate": round(prediction, 2),
            "confidence": "high" if prediction > 0 else "low"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/messages/urgent")
async def get_urgent_messages_summary(current_user = Depends(get_current_user)):
    """Get AI summary of urgent messages (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        agent = MessageAgent("MessageAgent", llm_client)
        summary = await agent.route_urgent()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/actions/history")
async def get_agent_actions(current_user = Depends(get_current_user)):
    """Get history of agent actions"""
    try:
        db = await get_database()
        actions = await db.agent_actions.find({}).sort("_id", -1).limit(50).to_list(length=50)
        return {"actions": actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
