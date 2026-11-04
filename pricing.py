"""Прозрачные правила предварительного расчёта для MVP."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

TARIFFS = {
    "375": {"cat1": 3650, "cat2": 3500, "cat3": 3100},
    "585": {"cat1": 6100, "cat2": 5600, "cat3": 4750},
    "750": {"cat1": 6850, "cat2": 6500, "cat3": 5800},
}

ITEM_TYPES = {"кольцо", "серьги", "браслет", "кулон", "цепь", "колье"}
DAILY_INTEREST_RATE = Decimal("0.0029")
CRITICAL_DEFECT_KEYWORDS = (
    "разлом", "разорван", "разрыв", "сломан", "трещина", "треснут",
    "деформация", "погнут", "оплавлен", "расплавлен", "отсутству",
    "обломан", "обрыв", "порван", "распил", "распаян", "лопнул",
)


def normalize_item_type(item_type: Any) -> str:
    normalized = str(item_type).strip().lower()
    return normalized if normalized in ITEM_TYPES else "—"


def determine_category(condition: Any) -> str:
    normalized = str(condition).strip().lower()
    if normalized in {"плохое", "плохая", "плохой"}:
        return "cat3"
    if normalized in {"среднее", "средняя", "средний"}:
        return "cat2"
    return "cat1"


def _weight(value: Any) -> Decimal:
    if value in (None, "", 0):
        return Decimal("0")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("Вес должен быть числом") from error
    if parsed < 0:
        raise ValueError("Вес не может быть отрицательным")
    return parsed.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_price(form_data: dict[str, Any]) -> dict[str, Any]:
    """Рассчитывает предварительную сумму займа по тарифной сетке MVP."""
    fineness_key = str(form_data.get("fineness", "585"))
    if fineness_key not in TARIFFS:
        raise ValueError(f"Неподдерживаемая проба: {fineness_key}")

    weight = _weight(form_data.get("weight"))
    category = determine_category(form_data.get("condition", "Среднее"))
    price_per_gram = TARIFFS[fineness_key][category]
    loan_amount = (
        int((Decimal(price_per_gram) * weight).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        if weight > 0
        else None
    )

    return {
        "item_type": normalize_item_type(form_data.get("item_type", "")),
        "fineness_key": fineness_key,
        "has_inserts": bool(form_data.get("has_inserts", False)),
        "condition": form_data.get("condition", "Среднее"),
        "price_per_gram": price_per_gram,
        "weight": float(weight),
        "loan_amount": loan_amount,
        "buyout_amount": loan_amount,
        "daily_interest_rate": float(DAILY_INTEREST_RATE * 100),
    }


def _looks_critical(text: Any) -> bool:
    normalized = str(text).strip().lower()
    return any(keyword in normalized for keyword in CRITICAL_DEFECT_KEYWORDS)


def acceptance_probability(form_data: dict[str, Any]) -> dict[str, Any]:
    """Возвращает объяснимую эвристическую вероятность приёма (0–100%)."""
    score = 100
    reasons: list[str] = []
    condition = str(form_data.get("condition", "Среднее")).strip().lower()
    severity = str(form_data.get("defect_severity", "нет")).strip().lower()
    repairable = bool(form_data.get("repairable", True))
    has_defects = bool(form_data.get("has_defects", False))
    insert_damage = bool(form_data.get("insert_damage", False))
    defects_description = str(form_data.get("defects_description", ""))

    if severity != "критичный" and _looks_critical(defects_description):
        severity = "критичный"

    if condition in {"плохое", "плохая", "плохой"}:
        score -= 50
        reasons.append("Плохое состояние изделия")
    elif condition in {"среднее", "средняя", "средний"}:
        score -= 20
        reasons.append("Среднее состояние: возможны следы износа")

    description = defects_description if defects_description and defects_description != "—" else ""
    if severity == "критичный":
        score -= 75
        reasons.append(f"Критичный дефект: {description}" if description else "Критичный дефект: приём только на лом")
    elif severity == "средний":
        score -= 30
        reasons.append(f"Дефекты средней тяжести: {description}" if description else "Заметные дефекты")
    elif severity == "незначительный":
        score -= 10
        reasons.append(f"Незначительные дефекты: {description}" if description else "Мелкие дефекты")
    elif has_defects:
        score -= 25
        reasons.append(f"Видимые дефекты: {description}" if description else "Видимые дефекты")

    if not repairable:
        score -= 15
        reasons.append("Изделие неремонтопригодно: возможен приём только на лом")

    if insert_damage:
        score -= 30
        reasons.append("Повреждены вставки (камни)")
    elif form_data.get("has_inserts"):
        score -= 10
        reasons.append("Вставки требуют отдельной оценки")

    if _weight(form_data.get("weight")) <= 0:
        score -= 5
        reasons.append("Вес не указан: расчёт нельзя выполнить точно")

    score = max(0, min(100, score))
    verdict = (
        "Высокая вероятность приёма" if score >= 75 else
        "Средняя вероятность приёма" if score >= 45 else
        "Низкая вероятность приёма" if score >= 20 else
        "Приём маловероятен"
    )
    return {"probability": score, "verdict": verdict, "reasons": reasons or ["Замечаний не выявлено"]}
