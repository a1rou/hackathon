import os
from dotenv import load_dotenv

load_dotenv()

TARIFFS = {
    "375": {
        "cat1": 3650,
        "cat2": 3500,
        "cat3": 3100,
    },
    "585": {
        "cat1": 6100,
        "cat2": 5600,
        "cat3": 4750,
    },
    "750": {
        "cat1": 6850,
        "cat2": 6500,
        "cat3": 5800,
    },
}

ITEM_TYPES = {"кольцо", "серьги", "браслет", "кулон", "цепь", "колье"}

def normalize_item_type(item_type: str) -> str:
    t = str(item_type).strip().lower()
    return t if t in ITEM_TYPES else "—"


def determine_category(condition: str) -> str:
    cond = str(condition).strip().lower()
    if cond in ("плохое", "плохая", "плохой"):
        return "cat3"
    if cond in ("среднее", "средняя", "средний"):
        return "cat2"
    return "cat1"


def calculate_price(form_data: dict) -> dict:
    """
    Рассчитывает предварительную стоимость изделия.

    form_data ожидает:
      item_type (str)   — тип изделия
      fineness (str)    — проба ("375", "585", "750")
      has_inserts (bool)— наличие вставок
      condition (str)   — состояние ("как новое" / "среднее" / "плохое")
      weight (float)    — вес в граммах (необязательное поле)
    """
    item_type    = normalize_item_type(form_data.get("item_type", ""))
    fineness_key = form_data.get("fineness", "585")
    has_inserts  = bool(form_data.get("has_inserts", False))
    condition    = form_data.get("condition", "среднее")

    weight_raw = form_data.get("weight", None)
    weight = float(weight_raw) if weight_raw not in (None, "", 0) else 0.0

    category      = determine_category(condition)
    price_per_gram = TARIFFS[fineness_key][category]

    if weight > 0:
        loan_amount  = round(price_per_gram * weight)
        buyout_amount = loan_amount
    else:
        loan_amount   = None
        buyout_amount = None

    return {
        "item_type":      item_type,
        "fineness_key":   fineness_key,
        "has_inserts":    has_inserts,
        "condition":      condition,
        "price_per_gram": price_per_gram,
        "weight":         weight,
        "loan_amount":    loan_amount,
        "buyout_amount":  buyout_amount,
    }


# страховочные ключевые слова критичных дефектов
CRITICAL_DEFECT_KEYWORDS = (
    "разлом", "разорван", "разрыв", "сломан", "трещина", "треснут",
    "деформация", "погнут", "оплавлен", "расплавлен", "отсутству",
    "обломан", "обрыв", "порван", "распил", "распаян", "лопнул",
)


def _looks_critical(text: str) -> bool:
    t = str(text).strip().lower()
    return any(k in t for k in CRITICAL_DEFECT_KEYWORDS)


def acceptance_probability(form_data: dict) -> dict:
    """Оценивает вероятность приёма изделия (0..100%)."""
    score   = 100
    reasons = []

    condition           = str(form_data.get("condition", "среднее")).strip().lower()
    severity            = str(form_data.get("defect_severity", "нет")).strip().lower()
    repairable          = bool(form_data.get("repairable", True))
    has_defects         = bool(form_data.get("has_defects", False))
    insert_damage       = bool(form_data.get("insert_damage", False))
    defects_description = str(form_data.get("defects_description", ""))

    if severity != "критичный" and _looks_critical(defects_description):
        severity = "критичный"

    # --- Состояние ---
    if condition in ("плохое", "плохая", "плохой"):
        score -= 50
        reasons.append("Плохое состояние изделия")
    elif condition in ("среднее", "средняя", "средний"):
        score -= 20
        reasons.append("Среднее состояние (следы износа)")

    # --- Серьёзность дефектов ---
    descr = (defects_description
             if defects_description and defects_description != "—" else "")
    if severity == "критичный":
        score -= 75
        reasons.append(
            f"Критичный дефект: {descr}" if descr
            else "Критичный дефект — изделие принимается только на лом"
        )
    elif severity == "средний":
        score -= 30
        reasons.append(f"Дефекты средней тяжести: {descr}" if descr else "Заметные дефекты")
    elif severity == "незначительный":
        score -= 10
        reasons.append(f"Незначительные дефекты: {descr}" if descr else "Мелкие дефекты")
    elif has_defects:
        score -= 25
        reasons.append(f"Дефекты: {descr}" if descr else "Видимые дефекты")

    # --- Неремонтопригодность ---
    if not repairable:
        score -= 15
        reasons.append("Изделие неремонтопригодно (приём только на лом)")

    # --- Повреждение вставок ---
    if insert_damage:
        score -= 30
        reasons.append("Повреждены вставки (камни)")
    elif form_data.get("has_inserts"):
        score -= 10
        reasons.append("Наличие вставок (требуется отдельная оценка)")

    # --- Вес ---
    weight_raw = form_data.get("weight", None)
    weight = float(weight_raw) if weight_raw not in (None, "", 0) else 0.0
    if weight <= 0:
        score -= 5
        reasons.append("Вес не указан — расчёт приблизительный")

    score = max(0, min(100, score))

    if score >= 75:
        verdict = "Высокая вероятность приёма"
    elif score >= 45:
        verdict = "Средняя вероятность приёма"
    elif score >= 20:
        verdict = "Низкая вероятность приёма"
    else:
        verdict = "Приём маловероятен"

    return {
        "probability": score,
        "verdict":     verdict,
        "reasons":     reasons or ["Замечаний не выявлено"],
    }