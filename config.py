import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("RAMP_CLIENT_ID")
CLIENT_SECRET = os.getenv("RAMP_CLIENT_SECRET")

BASE_URL = os.getenv(
    "RAMP_BASE_URL",
    "https://api.ramp.com"
)
