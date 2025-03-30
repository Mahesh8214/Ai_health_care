import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("AIzaSyBGw47E4QS_xQXKEhVh_2F5u-bOpk-31wg")
    GROQ_API_KEY = os.getenv("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")
    NEWS_API_KEY = os.getenv("f0ebe21314e54bf59eaa87cdeb3f16be")
    
    class Config:
        env_file = ".env"

settings = Settings()