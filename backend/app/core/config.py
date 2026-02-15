"""
Configuration management for the Resume Builder System
Handles environment variables and application settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Application Configuration
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx"}
    
    # Resume Configuration
    RESUME_TEMPLATES: list = ["professional", "modern", "classic"]
    
    @classmethod
    def validate(cls):
        """Validate that all required settings are present"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in .env file")
        return True

settings = Settings()