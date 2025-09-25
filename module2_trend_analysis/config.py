from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch values from environment
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
