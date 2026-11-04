"""Адаптер создания обращения: demo-режим или webhook Битрикс24."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from config import settings

logger = logging.getLogger(__name__)


def _build_payload(
    client_name: str,
    client_phone: str,
    analysis: dict[str, Any],
    price: dict[str, Any],
    prob: dict[str, Any],
    photos_count: int,
) -> dict[str, Any]:
    """Формирует единый payload; пользовательские поля нужно создать в CRM заранее."""
    return {
        "fields": {
            "TITLE": f"Предварительная оценка — {analysis.get('type', 'изделие')}",
            "COMMENTS": (
                f"Клиент: {client_name}\nТелефон: {client_phone}\n"
                f"Создано: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
                f"Фото: {photos_count}\nИсточник анализа: {analysis.get('analysis_source', '—')}"
            ),
            "UF_ITEM_TYPE": analysis.get("type", "—"),
            "UF_HAS_INSERTS": "Да" if analysis.get("has_inserts") else "Нет",
            "UF_CONDITION": analysis.get("condition", "—"),
            "UF_DEFECTS_DESCR": analysis.get("defects_description", "—"),
            "UF_DEFECT_SEVERITY": analysis.get("defect_severity", "—"),
            "UF_WEIGHT_G": analysis.get("estimated_weight_g", "—"),
            "UF_WEIGHT_SOURCE": analysis.get("weight_source", "—"),
            "UF_PRICE_PER_GRAM": price.get("price_per_gram"),
            "UF_LOAN_AMOUNT": price.get("loan_amount"),
            "UF_BUYOUT_AMOUNT": price.get("buyout_amount"),
            "UF_DAILY_INTEREST_RATE": price.get("daily_interest_rate"),
            "UF_ACCEPT_PROB": prob.get("probability"),
            "UF_ACCEPT_VERDICT": prob.get("verdict"),
            "UF_PHOTOS_COUNT": photos_count,
        }
    }


def _send_to_bitrix(payload: dict[str, Any]) -> int:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        settings.bitrix_webhook_url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:  # nosec B310: webhook is operator-configured
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        logger.warning("Ошибка интеграции Bitrix24: %s", type(error).__name__)
        raise RuntimeError("CRM временно недоступна") from error

    deal_id = data.get("result")
    if not deal_id:
        logger.warning("Bitrix24 вернул ответ без идентификатора сделки")
        raise RuntimeError("CRM не подтвердила создание обращения")
    return int(deal_id)


def create_deal(
    client_name: str,
    client_phone: str,
    analysis: dict[str, Any],
    price: dict[str, Any],
    prob: dict[str, Any],
    photos_count: int = 0,
) -> dict[str, Any]:
    """Создаёт CRM-сделку или демонстрационный номер без отправки персональных данных."""
    payload = _build_payload(client_name, client_phone, analysis, price, prob, photos_count)

    if not settings.bitrix_enabled:
        return {
            "success": True,
            "deal_id": f"DEMO-{uuid4().hex[:8].upper()}",
            "payload": payload,
            "mode": "demo",
            "message": "Демо-режим: данные не были переданы во внешнюю CRM",
        }

    try:
        return {
            "success": True,
            "deal_id": _send_to_bitrix(payload),
            "payload": payload,
            "mode": "production",
            "message": "Обращение передано в CRM",
        }
    except RuntimeError as error:
        return {"success": False, "deal_id": None, "payload": payload, "mode": "production", "message": str(error)}
