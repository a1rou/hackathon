"""Настройки приложения и интеграций из переменных окружения."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    yc_api_key: str | None
    yc_folder_id: str | None
    bitrix_webhook_url: str | None

    @property
    def ai_enabled(self) -> bool:
        return bool(self.yc_api_key and self.yc_folder_id)

    @property
    def model_name(self) -> str | None:
        if not self.yc_folder_id:
            return None
        return f"gpt://{self.yc_folder_id}/qwen3.6-35b-a3b/latest"

    @property
    def bitrix_enabled(self) -> bool:
        return bool(self.bitrix_webhook_url)


settings = Settings(
    yc_api_key=os.getenv("YC_API_KEY"),
    yc_folder_id=os.getenv("YC_FOLDER_ID"),
    bitrix_webhook_url=os.getenv("BITRIX_WEBHOOK_URL"),
)

BASE_URL = "https://ai.api.cloud.yandex.net/v1"
