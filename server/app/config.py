import os
import sys
import logging
import re

from dotenv import load_dotenv
from sympy.printing.pytorch import torch

load_dotenv()

# --- Logging Configuration ---
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app")

# --- Constants & Secrets ---
CLIENT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,50}$")
CONTROLLER_ID = "LLM"
LLM_SECRET_TOKEN = os.environ.get("LLM_SECRET_TOKEN")
UNITY_CLIENT_TOKEN = os.environ.get("UNITY_CLIENT_TOKEN")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@redis:6379/0"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
WHISPER_MODEL_SIZE = "large-v3"


# --- Startup Check ---
def check_keys():
    if not LLM_SECRET_TOKEN or not UNITY_CLIENT_TOKEN:
        logger.critical("Security keys are missing from environment variables.")
        sys.exit(1)

    if not REDIS_PASSWORD:
        logger.critical("REDIS_PASSWORD is missing from environment variables.")
        sys.exit(1)
