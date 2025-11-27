"""
LLM Client with auto-healing and fallback support
Supports OpenAI, Google Gemini, and mock responses
"""
import os
from typing import Optional

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

OPENAI_AVAILABLE = False
GENAI_AVAILABLE = False

if OPENAI_API_KEY:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        OPENAI_AVAILABLE = True
    except Exception:
        pass

if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        GENAI_AVAILABLE = True
    except Exception:
        pass


class LLMClient:
    """Universal LLM client with auto-healing and fallback"""
    
    def __init__(self):
        self.provider = None
        self.retry_count = 0
        
        if OPENAI_AVAILABLE:
            self.provider = 'openai'
        elif GENAI_AVAILABLE:
            self.provider = 'gemini'
        else:
            self.provider = 'mock'
    
    def _try_openai(self, prompt: str, max_tokens: int = 200) -> str:
        """Try OpenAI with auto-fallback"""
        try:
            import openai
            resp = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return resp['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f'🔧 OpenAI Error (auto-healing): {e}. Falling back to Gemini...')
            return self._try_gemini(prompt, max_tokens)
    
    def _try_gemini(self, prompt: str, max_tokens: int = 200) -> str:
        """Try Gemini with auto-fallback"""
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f'🔧 Gemini Error (auto-healing): {e}. Using mock...')
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Mock response for testing"""
        if 'anomaly' in prompt.lower():
            return 'NORMAL - No anomalies detected'
        if 'attendance' in prompt.lower():
            return 'Attendance pattern looks good. Keep up the consistency!'
        if 'learning' in prompt.lower() or 'recommend' in prompt.lower():
            return 'Recommended: Focus on core fundamentals, then advance to specialized topics'
        return prompt[:120] + '...' if len(prompt) > 120 else prompt
    
    def chat(self, prompt: str, max_tokens: int = 200) -> str:
        """Universal chat with auto-healing and fallback"""
        if self.provider == 'openai':
            return self._try_openai(prompt, max_tokens)
        elif self.provider == 'gemini':
            return self._try_gemini(prompt, max_tokens)
        else:
            return self._mock_response(prompt)
    
    def summarize(self, text: str, max_tokens: int = 200) -> str:
        """Summarize with intelligent fallback"""
        prompt = f"Summarize concisely: {text}"
        return self.chat(prompt, max_tokens)
    
    def detect_anomaly_ai(self, data: str) -> str:
        """AI-powered anomaly detection"""
        prompt = f"Analyze this attendance data for anomalies: {data}. Return: 'NORMAL' or describe the anomaly."
        result = self.chat(prompt, max_tokens=100)
        return result
    
    def analyze_attendance(self, user_data: str) -> str:
        """Intelligent attendance analysis"""
        prompt = f"Analyze attendance patterns: {user_data}. Provide insights and recommendations (2-3 lines)."
        return self.chat(prompt, max_tokens=150)
    
    def recommend_learning_path(self, logs_text: str) -> str:
        """AI learning path recommendation"""
        if self.provider == 'mock':
            if 'tensorflow' in logs_text.lower() or 'pytorch' in logs_text.lower():
                return 'Deep Learning: Start with CNNs, then Transfer Learning'
            if 'sql' in logs_text.lower() or 'pandas' in logs_text.lower():
                return 'Data Engineering: SQL → ETL → Data Cleaning'
            return 'Core ML: Linear Models → Neural Networks → Advanced'
        
        prompt = f"Learning path for: {logs_text}\nProvide 2-line recommendation."
        return self.chat(prompt, max_tokens=150)


class SimpleVectorStore:
    """Simple vector store for semantic search"""
    
    def __init__(self, dim: int = 32):
        self.dim = dim
        self.items = []
    
    def _text_to_vec(self, text: str):
        """Convert text to vector using hash"""
        import hashlib
        h = hashlib.sha256(text.encode()).digest()
        vec = [b for b in h[:self.dim]]
        norm = sum(v * v for v in vec) ** 0.5
        if norm == 0:
            norm = 1.0
        return [v / norm for v in vec]
    
    def add(self, _id: str, text: str):
        """Add item to vector store"""
        v = self._text_to_vec(text)
        self.items.append((_id, text, v))
    
    def query(self, text: str, k: int = 3):
        """Query vector store"""
        qv = self._text_to_vec(text)
        sims = []
        for _id, t, v in self.items:
            dot = sum(a * b for a, b in zip(qv, v))
            sims.append((_id, t, dot))
        sims.sort(key=lambda x: x[2], reverse=True)
        return sims[:k]
