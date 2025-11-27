from backend.modules.ai.llm import llm_service
from typing import List, Dict, Any

class ReportAgent:
    async def generate_daily_report(self, date: str, data: List[Dict[str, Any]]) -> str:
        prompt = f"Generate a daily attendance report for {date}."
        return await llm_service.generate_response(prompt, str(data))

class AlertAgent:
    async def check_anomalies(self, data: List[Dict[str, Any]]) -> List[str]:
        # Logic to detect anomalies using LLM or rules
        return []

report_agent = ReportAgent()
alert_agent = AlertAgent()
