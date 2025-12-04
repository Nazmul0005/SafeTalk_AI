import os
from dotenv import load_dotenv
            
load_dotenv()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            cls._instance.WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "whisper-1")
        return cls._instance
    
