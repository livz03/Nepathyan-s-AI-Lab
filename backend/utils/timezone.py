"""
Nepal Timezone Utilities
Provides timezone-aware datetime functions for Nepal (UTC+5:45)
"""
from datetime import datetime, date, time
import pytz

# Nepal Timezone (GMT+5:45)
NEPAL_TZ = pytz.timezone('Asia/Kathmandu')

def get_nepal_time() -> datetime:
    """Get current time in Nepal timezone"""
    return datetime.now(NEPAL_TZ)

def get_nepal_date() -> date:
    """Get current date in Nepal timezone"""
    return get_nepal_time().date()

def get_nepal_time_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Get current Nepal time as formatted string"""
    return get_nepal_time().strftime(fmt)

def to_nepal_time(dt: datetime) -> datetime:
    """Convert any datetime to Nepal timezone"""
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(NEPAL_TZ)

def is_lab_open() -> bool:
    """
    Check if lab is currently open
    Lab hours: 12:00 PM - 5:00 PM Nepal Time
    """
    current_hour = get_nepal_time().hour
    return 12 <= current_hour < 17

def get_lab_status() -> str:
    """Get lab status: OPEN or CLOSED"""
    return "OPEN" if is_lab_open() else "CLOSED"

def get_lab_hours_info() -> dict:
    """Get lab hours information"""
    return {
        "open_time": "12:00 PM",
        "close_time": "5:00 PM",
        "timezone": "Nepal Time (UTC+5:45)",
        "current_status": get_lab_status(),
        "current_time": get_nepal_time_str("%I:%M %p")
    }

def validate_lab_hours(operation: str = "check-in") -> tuple[bool, str]:
    """
    Validate if current time is within lab hours
    Returns: (is_valid, message)
    """
    current_hour = get_nepal_time().hour
    current_time = get_nepal_time_str("%I:%M %p")
    
    if operation == "check-in":
        if current_hour < 12:
            return False, f"❌ Lab not open yet. Opens at 12:00 PM. Current time: {current_time}"
        elif current_hour >= 17:
            return False, f"❌ Lab closed. Hours: 12:00 PM - 5:00 PM. Current time: {current_time}"
        else:
            return True, f"✅ Lab is open. Current time: {current_time}"
    
    # Check-out can happen anytime after check-in
    return True, f"✅ Check-out allowed. Current time: {current_time}"

def get_today_date_str() -> str:
    """Get today's date in YYYY-MM-DD format (Nepal timezone)"""
    return get_nepal_date().strftime("%Y-%m-%d")

def parse_nepal_datetime(date_str: str, time_str: str = "00:00:00") -> datetime:
    """Parse date and time strings into Nepal timezone datetime"""
    dt_str = f"{date_str} {time_str}"
    naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    return NEPAL_TZ.localize(naive_dt)
