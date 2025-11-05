import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
