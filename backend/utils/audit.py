"""
Audit Logging Utility
Tracks all important system actions for security and compliance
"""
from backend.database.connection import get_database
from backend.utils.timezone import get_nepal_time_str
from typing import Optional

async def log_audit(actor: str, action: str, details: Optional[dict] = None):
    """
    Log an audit event
    
    Args:
        actor: Username or user ID performing the action
        action: Description of the action
        details: Optional additional details as dict
    """
    try:
        db = await get_database()
        
        audit_entry = {
            "actor": actor,
            "action": action,
            "details": details or {},
            "timestamp": get_nepal_time_str()
        }
        
        await db.audit_logs.insert_one(audit_entry)
    except Exception as e:
        # Don't fail the main operation if audit logging fails
        print(f"Audit logging error: {e}")

async def get_audit_logs(limit: int = 100, actor: Optional[str] = None):
    """
    Retrieve audit logs
    
    Args:
        limit: Maximum number of logs to retrieve
        actor: Optional filter by actor
    """
    try:
        db = await get_database()
        
        query = {}
        if actor:
            query["actor"] = actor
        
        cursor = db.audit_logs.find(query).sort("timestamp", -1).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        return logs
    except Exception as e:
        print(f"Error retrieving audit logs: {e}")
        return []
