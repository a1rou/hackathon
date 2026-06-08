import base64
import json
import openai
from config import YC_API_KEY, BASE_URL, MODEL_NAME


client = openai.OpenAI(api_key=YC_API_KEY, base_url=BASE_URL)


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
"estimated_weight_g": число — оценочный вес изделия в граммах (например 3.5),
"weight_min_g": число — нижняя граница диапазона веса в граммах,
"weight_max_g": число — верхняя граница диапазона веса в граммах,
"weight_confidence": "высокая|средняя|низкая",
"weight_reasoning": "краткое обоснование оценки веса на русском"
}

Правила оценки состояния:
"Как новое" — нет видимых царапин и потёртостей, изделие блестит.
"Среднее" — есть мелкие царапины/потёртости.
"Плохое" — глубокие царапины, деформация, сильный износ.

Оценивай: царапины, потёртости, деформацию, повреждения вставок (камней).

Правила оценки серьёзности дефектов (defect_severity):
- "нет" — дефектов не выявлено.
- "незначительный" — мелкие царапины, лёгкие потёртости, не влияют на целостность.
- "средний" — заметный износ, потемнение, мелкие вмятины, без нарушения конструкции.
- "критичный" — нарушена целостность или конструкция изделия: разлом, разрыв,
  трещина насквозь, сильная деформация, оплавление, отсутствие части изделия,
  обрыв цепи/звена. Такие изделия принимают только на лом.
- "repairable": false, если изделие можно принять только на лом (критичный дефект),
  иначе true.

Правила оценки веса:
- Оценивай вес ТОЛЬКО на основе визуального размера, типа изделия,
  толщины металла, массивности и наличия вставок.
- Если есть эталон масштаба (рука, монета, линейка) — используй его.
- Учитывай типичные диапазоны веса для золотых изделий:
  тонкое кольцо 1-3 г, массивное кольцо 4-10 г, серьги 1-5 г за пару,
  тонкая цепь 2-6 г, массивная цепь 8-30 г, браслет 5-25 г, кулон 1-8 г.
- Если вставки крупные — вес самого металла может быть меньше общего.
- Указывай "weight_confidence": "низкая", если масштаб определить трудно.
- НЕ завышай точность — это приблизительная визуальная оценка.

Отвечай ТОЛЬКО валидным JSON на русском языке."""


def _encode(img_bytes: bytes) -> str:
    b64 = base64.b64encode(img_bytes).decode()
    return f"data:image/jpeg;base64,{b64}"


def analyze_jewelry(image_bytes_list: list[bytes], form_data: dict) -> dict:
    if not image_bytes_list:
        return _fallback(form_data)

    content = [{"type": "text", "text": PROMPT}]
    for img in image_bytes_list:
        content.append({
            "type": "image_url",
            "image_url": {"url": _encode(img)}
        })

    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": content}],
            temperature=0.2,
            max_tokens=2000,
            extra_body={'reasoning_effort': 'none'}
        )
        text = resp.choices[0].message.content.strip()
        data = json.loads(text)
        return _normalize(data, form_data)
    except Exception as e:
        print("AI error:", e)
        return _fallback(form_data)


def _to_float(value, default=None):
    """Безопасное преобразование к float."""
    try:
        if value is None:
            return default
        return round(float(value), 2)
    except (TypeError, ValueError):
        return default


def _normalize(data: dict, form_data: dict) -> dict:
    form_weight = _to_float(form_data.get("weight_g"))

    est_weight = _to_float(data.get("estimated_weight_g"))
    w_min = _to_float(data.get("weight_min_g"))
    w_max = _to_float(data.get("weight_max_g"))

    if form_weight is not None:
        final_weight = form_weight
        weight_source = "анкета (точный вес)"
        weight_confidence = "высокая"
    else:
        final_weight = est_weight
        weight_source = "оценка по фото"
        weight_confidence = data.get("weight_confidence") or "низкая"

    # нормализуем серьёзность дефекта
    severity = str(data.get("defect_severity", "нет")).strip().lower()
    if severity not in ("нет", "незначительный", "средний", "критичный"):
        severity = "нет"

    return {
        "type": data.get("type") or form_data.get("type", "Кольцо"),
        "has_inserts": bool(data.get("has_inserts", form_data.get("has_inserts", False))),
        "condition": data.get("condition") or form_data.get("condition", "Среднее"),
        "has_defects": bool(data.get("has_defects", False)),
        "defects_description": data.get("defects_description") or "—",
        "defect_severity": severity,
        "repairable": bool(data.get("repairable", True)),
        "insert_damage": bool(data.get("insert_damage", False)),
        "visual_notes": data.get("visual_notes") or "—",
        # --- блок веса ---
        "estimated_weight_g": final_weight,
        "weight_min_g": w_min,
        "weight_max_g": w_max,
        "weight_confidence": weight_confidence,
        "weight_source": weight_source,
        "weight_reasoning": data.get("weight_reasoning") or "—",
    }


def _fallback(form_data: dict) -> dict:
    form_weight = _to_float(form_data.get("weight_g"))

    return {
        "type": form_data.get("type", "Кольцо"),
        "has_inserts": form_data.get("has_inserts", False),
        "condition": form_data.get("condition", "Среднее"),
        "has_defects": False,
        "defects_description": "Анализ по анкете (фото не предоставлено)",
        "defect_severity": "нет",
        "repairable": True,
        "insert_damage": False,
        "visual_notes": "—",
        # --- блок веса ---
        "estimated_weight_g": form_weight,
        "weight_min_g": form_weight,
        "weight_max_g": form_weight,
        "weight_confidence": "высокая" if form_weight is not None else "нет данных",
        "weight_source": "анкета" if form_weight is not None else "нет данных",
        "weight_reasoning": "Вес взят из анкеты" if form_weight is not None
                            else "Вес не указан и фото не предоставлено",
    }