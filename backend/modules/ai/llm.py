import os
from typing import List, Dict, Any
import openai
import google.generativeai as genai
from backend.config import get_settings

settings = get_settings()

class LLMService:
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY
        
        if self.openai_key:
            openai.api_key = self.openai_key
            
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        # Try OpenAI first, then Gemini, then fallback
        if self.openai_key:
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant for an attendance system."},
                        {"role": "user", "content": f"Context: {context}\n\nPrompt: {prompt}"}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI Error: {e}")
                
        if self.gemini_key:
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(f"Context: {context}\n\nPrompt: {prompt}")
                return response.text
            except Exception as e:
                print(f"Gemini Error: {e}")

        return f"AI Response (Mock): {prompt} (Context: {context[:20]}...)"

    async def analyze_attendance(self, attendance_data: List[Dict[str, Any]], user_name: str) -> str:
        prompt = f"""
        Analyze the attendance data for {user_name}. 
        Identify trends, punctuality, and suggest improvements.
        Data: {attendance_data}
        Keep it concise and motivational.
        """
        return await self.generate_response(prompt)

llm_service = LLMService()
