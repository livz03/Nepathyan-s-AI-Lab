from datetime import datetime, timedelta
import numpy as np
from backend.database.connection import get_database
from typing import List, Dict, Any

async def get_user_attendance_history(user_id: str, days: int = 30) -> List[datetime]:
    db = await get_database()
    start_date = datetime.now() - timedelta(days=days)
    cursor = db.attendance.find({
        "user_id": user_id,
        "timestamp": {"$gte": start_date}
    }).sort("timestamp", 1)
    
    records = await cursor.to_list(length=1000)
    return [record["timestamp"] for record in records]

def calculate_anomaly_score(check_in_times: List[datetime]) -> float:
    if len(check_in_times) < 5:
        return 0.0
    
    # Convert times to minutes from midnight
    minutes = [t.hour * 60 + t.minute for t in check_in_times]
    
    # Calculate Z-score of the latest check-in
    mean = np.mean(minutes[:-1])
    std = np.std(minutes[:-1])
    
    if std == 0:
        return 0.0
        
    latest = minutes[-1]
    z_score = abs((latest - mean) / std)
    
    # Normalize to 0-1 range (clamped)
    anomaly_score = min(z_score / 3.0, 1.0)
    return float(anomaly_score)

def classify_pattern(check_in_times: List[datetime]) -> str:
    if len(check_in_times) < 5:
        return "Newcomer"
        
    minutes = [t.hour * 60 + t.minute for t in check_in_times]
    avg_time = np.mean(minutes)
    std_dev = np.std(minutes)
    
    # 9:00 AM = 540 minutes
    if std_dev < 30: # Very consistent
        if avg_time < 540: # Before 9 AM
            return "Early Bird"
        elif avg_time > 600: # After 10 AM
            return "Night Owl"
        else:
            return "Consistent"
    elif std_dev > 60:
        return "Flexible"
    else:
        return "Regular"

async def get_user_analytics(user_id: str) -> Dict[str, Any]:
    history = await get_user_attendance_history(user_id)
    
    if not history:
        return {
            "anomaly_score": 0.0,
            "pattern": "Newcomer",
            "streak": 0,
            "total_days": 0
        }
        
    anomaly_score = calculate_anomaly_score(history)
    pattern = classify_pattern(history)
    
    # Calculate streak
    streak = 0
    today = datetime.now().date()
    # Simplified streak logic
    # In real app, check consecutive days properly handling weekends
    
    return {
        "anomaly_score": anomaly_score,
        "pattern": pattern,
        "streak": len(history), # Placeholder for actual streak logic
        "total_days": len(history)
    }
