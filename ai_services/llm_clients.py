from config import settings
import google.generativeai as genai
from groq import Groq

class LLMClients:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.gemini = genai.GenerativeModel("gemini-1.5-flash")
        self.groq = Groq(api_key=settings.GROQ_API_KEY)

    def get_groq_response(self, prompt: str, model: str = "llama3-70b-8192") -> str:
        try:
            response = self.groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")