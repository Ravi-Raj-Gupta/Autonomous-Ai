# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     # LLM Configuration
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#     MODEL_NAME = "gpt-3.5-turbo"
    
#     # CrewAI Configuration
#     # CREW_MAX_ITERATIONS = 3
#     CREW_VERBOSE = True
    
#     # Tools Configuration
#     SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # Free tier available
    
#     # File Paths
#     OUTPUT_DIR = "outputs"
#     MEMORY_DIR = "memory"
    
#     @classmethod
#     def validate_config(cls):
#         """Validate required environment variables"""
#         if not cls.OPENAI_API_KEY:
#             raise ValueError("OPENAI_API_KEY not found in .env file")
#         return True

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-3.5-turbo"
    CREW_MAX_ITERATIONS = 3
    CREW_VERBOSE = True
    OUTPUT_DIR = "outputs"
    MEMORY_DIR = "memory"


