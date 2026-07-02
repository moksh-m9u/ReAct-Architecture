import os
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL", "qwen/qwen3-32b")
MAX_STEPS = int(os.getenv("MAX_STEPS", "10"))
