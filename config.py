import os
from dotenv import load_dotenv

load_dotenv()

YC_API_KEY = os.getenv("YC_API_KEY")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")
BASE_URL = "https://ai.api.cloud.yandex.net/v1"
MODEL_NAME = f"gpt://{YC_FOLDER_ID}/qwen3.6-35b-a3b/latest"