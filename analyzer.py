"""Мультимодальный анализ фотографии ювелирного изделия."""
from __future__ import annotations

import base64
import json
import logging
from collections.abc import Sequence
from typing import Any

from config import BASE_URL, settings

logger = logging.getLogger(__name__)

ITEM_TYPES = {"Кольцо", "Серьги", "Браслет", "Кулон", "Цепь", "Колье"}
CONDITIONS = {"Как новое", "Среднее", "Плохое"}
SEVERITIES = {"нет", "незначительный", "средний", "критичный"}
CONFIDENCE_LEVELS = {"высокая", "средняя", "низкая"}

PROMPT = """Ты — опытный товаровед ломбарда. Перед тобой фотографии
ЗОЛОТОГО ювелирного изделия. Внимательно осмотри изделие и верни СТРОГО
JSON без markdown и без пояснений:

{
  "type": "Кольцо|Серьги|Браслет|Кулон|Цепь|Колье",
  "has_inserts": true или false,
  "condition": "Как новое|Среднее|Плохое",
  "has_defects": true или false,
  "defects_description": "краткое описание дефектов на русском, либо 'не выявлено'",
  "defect_severity": "нет|незначительный|средний|критичный",
  "repairable": true или false,
  "insert_damage": true или false,
  "visual_notes": "иные заметные визуальные характеристики",
  "estimated_weight_g": число — оценочный вес изделия в граммах,
  "weight_min_g": число — нижняя граница диапазона веса в граммах,
  "weight_max_g": число — верхняя граница диапазона веса в граммах,
  "weight_confidence": "высокая|средняя|низкая",
  "weight_reasoning": "краткое обоснование оценки веса на русском"
}

Правила оценки состояния:
"Как новое" — нет видимых царапин и потёртостей, изделие блестит.
"Среднее" — есть мелкие царапины/потёртости.
"Плохое" — глубокие царапины, деформация, сильный износ.

Оценивай царапины, потёртости, деформацию и повреждения вставок.

Правила оценки серьёзности дефектов:
- "нет" — дефектов не выявлено.
- "незначительный" — мелкие царапины и лёгкие потёртости.
- "средний" — заметный износ, потемнение или мелкие вмятины без нарушения конструкции.
- "критичный" — нарушена целостность: разлом, разрыв, трещина, сильная деформация,
  оплавление или отсутствие части изделия. Такие изделия принимают только на лом.
- repairable=false, если изделие можно принять только на лом.

Правила оценки веса:
- Оценивай вес только по визуальному размеру, типу, толщине и массивности изделия.
- Используй эталон масштаба, если он есть на фото.
- Типичные диапазоны: тонкое кольцо 1–3 г, массивное кольцо 4–10 г, серьги 1–5 г
  за пару, тонкая цепь 2–6 г, массивная цепь 8–30 г, браслет 5–25 г, кулон 1–8 г.
- При крупных вставках вес металла может быть меньше общего веса.
- Не завышай точность: при отсутствии масштаба указывай низкую уверенность.

Отвечай только валидным JSON на русском языке."""


def _get_client() -> Any:
    """Создаёт клиента только для настоящего AI-запроса, не при импорте модуля."""
    if not settings.ai_enabled:
        raise RuntimeError("AI-анализ не настроен: добавьте YC_API_KEY и YC_FOLDER_ID")
    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError("Не установлена зависимость openai") from error
    return OpenAI(api_key=settings.yc_api_key, base_url=BASE_URL)


def _encode(image_bytes: bytes) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    media_type = "image/png" if image_bytes.startswith(b"\x89PNG\r\n\x1a\n") else "image/jpeg"
    return f"data:{media_type};base64,{encoded}"


def _extract_json(text: str) -> dict[str, Any]:
    """Извлекает объект из ответа модели, даже если тот окружил JSON markdown-блоком."""
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.split("\n", 1)[-1]
        candidate = candidate.rsplit("```", 1)[0].strip()

    start, end = candidate.find("{"), candidate.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Модель не вернула JSON-объект")

    parsed = json.loads(candidate[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Ответ модели должен быть JSON-объектом")
    return parsed


def analyze_jewelry(image_bytes_list: Sequence[bytes], form_data: dict[str, Any]) -> dict[str, Any]:
    """Анализирует до четырёх изображений и безопасно нормализует ответ модели.

    При недоступности модели возвращает расчёт по анкете, чтобы демо оставалось
    работоспособным и не выдавало неподтверждённый AI-результат за реальный.
    """
    if not image_bytes_list:
        return _fallback(form_data, "Фото не предоставлены")
    if len(image_bytes_list) > 4:
        raise ValueError("Можно загрузить не более четырёх фотографий")

    content: list[dict[str, Any]] = [{"type": "text", "text": PROMPT}]
    content.extend(
        {"type": "image_url", "image_url": {"url": _encode(image)}}
        for image in image_bytes_list
    )

    try:
        response = _get_client().chat.completions.create(
            model=settings.model_name,
            messages=[{"role": "user", "content": content}],
            temperature=0.2,
            max_tokens=1_500,
            extra_body={"reasoning_effort": "none"},
        )
        text = response.choices[0].message.content or ""
        return _normalize(_extract_json(text), form_data, source="ai")
    except Exception as error:  # API и ответ модели являются внешними зависимостями.
        logger.warning("AI-анализ недоступен: %s", type(error).__name__)
        return _fallback(form_data, "AI-анализ временно недоступен")


def _to_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or isinstance(value, bool):
            return default
        number = round(float(value), 2)
        return number if number >= 0 else default
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "да"}:
            return True
        if normalized in {"false", "0", "нет"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _allowed(value: Any, allowed: set[str], default: str) -> str:
    candidate = str(value).strip()
    return candidate if candidate in allowed else default


def _normalize(data: dict[str, Any], form_data: dict[str, Any], source: str = "ai") -> dict[str, Any]:
    form_weight = _to_float(form_data.get("weight_g"))
    estimated_weight = _to_float(data.get("estimated_weight_g"))
    weight_min = _to_float(data.get("weight_min_g"))
    weight_max = _to_float(data.get("weight_max_g"))

    if weight_min is not None and weight_max is not None and weight_min > weight_max:
        weight_min, weight_max = weight_max, weight_min

    if form_weight is not None:
        final_weight = form_weight
        weight_source = "анкета (точный вес)"
        weight_confidence = "высокая"
    else:
        final_weight = estimated_weight
        weight_source = "оценка по фото" if source == "ai" else "нет данных"
        weight_confidence = _allowed(data.get("weight_confidence"), CONFIDENCE_LEVELS, "низкая")

    condition = _allowed(data.get("condition"), CONDITIONS, form_data.get("condition", "Среднее"))
    severity = _allowed(data.get("defect_severity"), SEVERITIES, "нет")
    return {
        "type": _allowed(data.get("type"), ITEM_TYPES, form_data.get("type", "Кольцо")),
        "has_inserts": _to_bool(data.get("has_inserts"), bool(form_data.get("has_inserts"))),
        "condition": condition,
        "has_defects": _to_bool(data.get("has_defects")),
        "defects_description": str(data.get("defects_description") or "не выявлено").strip(),
        "defect_severity": severity,
        "repairable": _to_bool(data.get("repairable"), True),
        "insert_damage": _to_bool(data.get("insert_damage")),
        "visual_notes": str(data.get("visual_notes") or "—").strip(),
        "estimated_weight_g": final_weight,
        "weight_min_g": weight_min,
        "weight_max_g": weight_max,
        "weight_confidence": weight_confidence,
        "weight_source": weight_source,
        "weight_reasoning": str(data.get("weight_reasoning") or "—").strip(),
        "analysis_source": source,
    }


def _fallback(form_data: dict[str, Any], reason: str) -> dict[str, Any]:
    form_weight = _to_float(form_data.get("weight_g"))
    return {
        "type": _allowed(form_data.get("type"), ITEM_TYPES, "Кольцо"),
        "has_inserts": _to_bool(form_data.get("has_inserts")),
        "condition": _allowed(form_data.get("condition"), CONDITIONS, "Среднее"),
        "has_defects": False,
        "defects_description": reason,
        "defect_severity": "нет",
        "repairable": True,
        "insert_damage": False,
        "visual_notes": "—",
        "estimated_weight_g": form_weight,
        "weight_min_g": form_weight,
        "weight_max_g": form_weight,
        "weight_confidence": "высокая" if form_weight is not None else "нет данных",
        "weight_source": "анкета" if form_weight is not None else "нет данных",
        "weight_reasoning": "Вес указан клиентом" if form_weight is not None else reason,
        "analysis_source": "form",
    }
