"""
Заглушка интеграции с Битрикс24.
В реальном проекте здесь будет HTTP-запрос к REST API Битрикс24:
  POST https://<портал>.bitrix24.ru/rest/<user_id>/<token>/crm.deal.add
"""
from __future__ import annotations
import json
from datetime import datetime


def create_deal(
    client_name: str,
    client_phone: str,
    analysis: dict,
    price: dict,
    prob: dict,
    photos_count: int = 0,
) -> dict:
    """
    Имитирует создание сделки в Битрикс24.

    Возвращает словарь с результатом (success/error) и
    payload — тем, что было бы отправлено на сервер.
    """
    payload = {
        "fields": {
            # --- Клиент ---
            "TITLE":        f"Заявка ломбард — {client_name}",
            "NAME":         client_name,
            "PHONE":        client_phone,
            "CREATED_AT":   datetime.now().isoformat(timespec="seconds"),

            # --- Изделие ---
            "UF_ITEM_TYPE":       analysis.get("type", "—"),
            "UF_HAS_INSERTS":     "Да" if analysis.get("has_inserts") else "Нет",
            "UF_CONDITION":       analysis.get("condition", "—"),
            "UF_DEFECTS_DESCR":   analysis.get("defects_description", "—"),
            "UF_DEFECT_SEVERITY": analysis.get("defect_severity", "—"),
            "UF_WEIGHT_G":        analysis.get("estimated_weight_g", "—"),
            "UF_WEIGHT_SOURCE":   analysis.get("weight_source", "—"),

            # --- Расчёт ---
            "UF_PRICE_PER_GRAM":  price.get("price_per_gram"),
            "UF_TOTAL_VALUE":     price.get("total"),
            "UF_LOAN_AMOUNT":     price.get("loan_amount"),
            "UF_BUYOUT_AMOUNT":   price.get("buyout_amount"),

            # --- Вероятность ---
            "UF_ACCEPT_PROB":    prob.get("probability"),
            "UF_ACCEPT_VERDICT": prob.get("verdict"),

            # --- Фото ---
            "UF_PHOTOS_COUNT": photos_count,
            # В реальной интеграции сюда передаются base64 или ссылки на файлы
        }
    }

    # Заглушка
    fake_deal_id = 1001
    print("[Bitrix24 stub] Сделка создана (заглушка):")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    return {
        "success":  True,
        "deal_id":  fake_deal_id,
        "payload":  payload,
        "message":  "Сделка создана (режим заглушки — реальный запрос не отправлен)",
    }