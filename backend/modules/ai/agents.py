"""
AI Agents for attendance system
Includes: AttendanceAgent, ProgressAgent, SecurityAgent, PredictionAgent
"""
from backend.database.connection import get_database
from backend.modules.ai.llm_client import LLMClient
from datetime import datetime, timedelta, date
import json
import pytz

NEPAL_TZ = pytz.timezone('Asia/Kathmandu')


class Agent:
    """Base agent class"""
    
    def __init__(self, name: str, llm: LLMClient):
        self.name = name
        self.llm = llm
    
    async def log_action(self, action: str, payload: dict):
        """Log agent action to database"""
        try:
            db = await get_database()
            await db.agent_actions.insert_one({
                "agent_name": self.name,
                "action": action,
                "payload": json.dumps(payload),
                "timestamp": datetime.now(NEPAL_TZ)
            })
        except Exception as e:
            print(f"Agent log error: {e}")


class AttendanceAgent(Agent):
    """AI-powered attendance agent with self-healing"""
    
    async def self_heal_error(self, error: str, user_id: str, user_name: str) -> str:
        """🔧 Self-healing error recovery with AI"""
        print(f'🔧 AUTO-HEAL: Attempting to resolve error for {user_name}...')
        try:
            diagnosis = self.llm.chat(
                f"Error occurred: {error}. Suggest recovery for user {user_name}. Be brief.",
                max_tokens=50
            )
            await self.log_action('self_heal', {
                'user_id': user_id,
                'error': error,
                'diagnosis': diagnosis
            })
            return diagnosis
        except Exception as heal_err:
            print(f'🔧 Self-heal failed: {heal_err}')
            return "Error recovery attempted. Please retry."
    
    async def detect_anomaly(self, user_id: str, user_name: str) -> str:
        """🧠 AI-powered anomaly detection"""
        try:
            db = await get_database()
            recent = await db.attendance.find(
                {"user_id": user_id}
            ).sort("_id", -1).limit(20).to_list(length=20)
            
            if len(recent) < 3:
                return None
            
            times_text = '\n'.join([
                f"{r.get('check_in', 'N/A')} ({r.get('status', 'N/A')})"
                for r in recent[:5]
            ])
            
            anomaly = self.llm.detect_anomaly_ai(times_text)
            
            if 'NORMAL' not in anomaly.upper():
                await self.log_action('anomaly_detected', {
                    'user_id': user_id,
                    'name': user_name,
                    'anomaly': anomaly
                })
                return anomaly
            return None
        except Exception as e:
            await self.self_heal_error(str(e), user_id, user_name)
            return None
    
    async def get_attendance_insights(self, user_id: str, user_name: str) -> str:
        """🧠 AI-driven insights"""
        try:
            db = await get_database()
            today = datetime.now(NEPAL_TZ).date().isoformat()
            
            today_count = await db.attendance.count_documents({
                "user_id": user_id,
                "date": today
            })
            
            recent = await db.attendance.find(
                {"user_id": user_id}
            ).sort("_id", -1).limit(10).to_list(length=10)
            
            data = f"User: {user_name}, Today: {today_count} checkins, Recent: {[r.get('check_in', 'N/A') for r in recent[:3]]}"
            insight = self.llm.analyze_attendance(data)
            
            await self.log_action('attendance_insight', {
                'user_id': user_id,
                'name': user_name,
                'insight': insight
            })
            return insight
        except Exception as e:
            await self.self_heal_error(str(e), user_id, user_name)
            return "Attendance analysis ongoing..."


class ProgressAgent(Agent):
    """AI agent for learning progress and recommendations"""
    
    async def analyze_and_recommend(self, user_id: str) -> str:
        """Analyze work logs and recommend learning path"""
        try:
            db = await get_database()
            logs = await db.work_logs.find(
                {"user_id": user_id}
            ).sort("_id", -1).limit(10).to_list(length=10)
            
            logs_text = '\n'.join([log.get('raw_input', '') for log in logs if log.get('raw_input')])
            
            if not logs_text:
                rec = 'No logs found — suggest starting a beginner project in Python + Data.'
            else:
                rec = self.llm.recommend_learning_path(logs_text)
            
            await self.log_action('recommend_learning', {
                'user_id': user_id,
                'recommendation': rec
            })
            return rec
        except Exception as e:
            print(f"ProgressAgent error: {e}")
            return "Unable to generate recommendation at this time"


class SecurityAgent(Agent):
    """AI-powered security & anomaly detection"""
    
    async def detect_suspicious_pattern(self, user_id: str, user_name: str) -> str:
        """Detect suspicious attendance patterns"""
        try:
            db = await get_database()
            rows = await db.attendance.find(
                {"user_id": user_id}
            ).sort("_id", -1).limit(5).to_list(length=5)
            
            if len(rows) < 2:
                return 'SAFE'
            
            times_text = ','.join([
                f"{r.get('check_in', 'N/A')}-{r.get('check_out', 'N/A')}"
                for r in rows if r.get('check_in')
            ])
            
            prompt = f"Analyze entry/exit pattern for {user_name}: {times_text}. Return 'NORMAL' or 'SUSPICIOUS' (anomaly type)"
            result = self.llm.detect_anomaly_ai(times_text)
            
            await self.log_action('security_check', {
                'user_id': user_id,
                'name': user_name,
                'result': result
            })
            return result
        except Exception as e:
            print(f"SecurityAgent error: {e}")
            return 'SAFE'


class PredictionAgent(Agent):
    """AI-powered attendance prediction & forecasting"""
    
    async def predict_attendance_rate(self, user_id: str) -> float:
        """Predict next week attendance rate"""
        try:
            db = await get_database()
            
            present_count = await db.attendance.count_documents({
                "user_id": user_id,
                "status": "Present"
            })
            
            total_count = await db.attendance.count_documents({
                "user_id": user_id
            })
            
            if total_count == 0:
                return 50.0
            
            rate = (present_count / total_count) * 100
            
            prompt = f"Predict next week attendance. Current rate: {rate:.1f}%. History length: {total_count} days. Return percentage."
            prediction = self.llm.chat(prompt, max_tokens=50)
            
            try:
                # Extract number from response
                pred_value = float(''.join(filter(lambda x: x.isdigit() or x == '.', prediction.split('%')[0])))
                await self.log_action('prediction', {
                    'user_id': user_id,
                    'current_rate': rate,
                    'predicted_rate': pred_value
                })
                return pred_value
            except:
                return rate
        except Exception as e:
            print(f"PredictionAgent error: {e}")
            return 0.0


class MessageAgent(Agent):
    """AI agent for message routing and summarization"""
    
    async def route_urgent(self) -> str:
        """Route and summarize urgent messages"""
        try:
            db = await get_database()
            messages = await db.messages.find(
                {"is_urgent": 1}
            ).sort("_id", -1).limit(10).to_list(length=10)
            
            if not messages:
                return 'No urgent messages.'
            
            summary_text = '\n'.join([
                f"{msg.get('timestamp', 'N/A')} - {msg.get('sender_name', 'Unknown')}: {msg.get('message', '')}"
                for msg in messages
            ])
            
            summary = self.llm.summarize(summary_text, max_tokens=200)
            
            await self.log_action('route_urgent', {'summary': summary})
            return summary
        except Exception as e:
            print(f"MessageAgent error: {e}")
            return "Unable to process messages"
