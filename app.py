import re
from html import escape

import streamlit as st

from analyzer import analyze_jewelry
from bitrix import create_deal
from config import settings
from pricing import acceptance_probability, calculate_price

st.set_page_config(
    page_title="СКС Ломбард — Оценка украшений",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    :root {
        --canvas: #f8fafc;
        --paper: #ffffff;
        --ink: #020617;
        --muted: #475569;
        --quiet: #64748b;
        --line: #e2e8f0;
        --soft: #e8ecf1;
        --accent: #0f172a;
        --accent-hover: #334155;
        --gold: #0369a1;
        --positive-bg: #edf5ef;
        --positive-ink: #23623b;
        --medium-bg: #fbf1de;
        --medium-ink: #87570c;
        --low-bg: #f8eae7;
        --low-ink: #a23e31;
    }

    #MainMenu, footer { visibility: hidden !important; }

    .stApp {
        background: var(--canvas) !important;
        color: var(--ink) !important;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .block-container {
        max-width: 1160px !important;
        padding: 1.25rem 1.25rem 4rem !important;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 4rem;
        margin-bottom: 3.75rem;
        border-bottom: 1px solid var(--line);
    }

    .wordmark {
        display: inline-flex;
        align-items: center;
        gap: .7rem;
        color: var(--ink);
        font-size: .84rem;
        font-weight: 750;
        letter-spacing: .01em;
    }

    .wordmark-mark {
        display: grid;
        place-items: center;
        width: 1.6rem;
        height: 1.6rem;
        border-radius: 5px;
        background: var(--accent);
    }

    .wordmark-mark svg { width: .86rem; height: .86rem; fill: #fff; }

    .topbar-note {
        color: var(--muted);
        font-size: .76rem;
        font-weight: 600;
    }

    .hero {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: end;
        gap: 2rem;
        margin-bottom: 3.25rem;
    }

    .eyebrow {
        margin: 0 0 .85rem;
        color: var(--gold);
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
    }

    .hero h1 {
        max-width: 52rem;
        margin: 0;
        color: var(--ink);
        font-family: Iowan Old Style, Baskerville, Georgia, serif;
        font-size: clamp(2.6rem, 6.2vw, 5.3rem);
        font-weight: 500;
        letter-spacing: -.065em;
        line-height: .94;
    }

    .hero h1 em { color: var(--gold); font-style: normal; }

    .hero-copy {
        max-width: 38rem;
        margin: 1.3rem 0 0;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.65;
    }

    .trust-list {
        display: grid;
        gap: .7rem;
        min-width: 13.5rem;
        padding: 1rem 0 0 1.35rem;
        border-left: 1px solid var(--line);
    }

    .trust-item { color: var(--muted); font-size: .76rem; line-height: 1.35; }
    .trust-item strong { display: block; color: var(--ink); font-size: .8rem; font-weight: 700; }

    .workflow {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0;
        margin: 0 0 2rem;
        border: 1px solid var(--line);
        border-radius: 10px;
        overflow: hidden;
        background: var(--paper);
    }

    .workflow-step {
        display: flex;
        align-items: center;
        gap: .7rem;
        padding: .9rem 1rem;
        border-right: 1px solid var(--line);
        color: var(--muted);
        font-size: .76rem;
        font-weight: 600;
    }

    .workflow-step:last-child { border-right: 0; }
    .step-index {
        display: grid;
        place-items: center;
        width: 1.45rem;
        height: 1.45rem;
        border-radius: 50%;
        background: var(--soft);
        color: var(--ink);
        font-size: .68rem;
        font-weight: 800;
    }

    .panel {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 1.55rem;
    }

    .panel-heading {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .panel-title {
        margin: 0;
        color: var(--ink);
        font-size: 1rem;
        font-weight: 720;
        letter-spacing: -.025em;
    }

    .panel-caption { margin: .35rem 0 0; color: var(--muted); font-size: .82rem; line-height: 1.45; }
    .panel-index { color: var(--quiet); font-size: .72rem; font-weight: 750; letter-spacing: .08em; }

    .form-section-label {
        display: flex;
        align-items: center;
        gap: .6rem;
        margin: 1.65rem 0 .85rem;
        color: var(--ink);
        font-size: .78rem;
        font-weight: 750;
    }

    .form-section-label::after { content: ""; height: 1px; flex: 1; background: var(--line); }

    .result-empty {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        min-height: 29rem;
        padding: 1.7rem;
        border: 1px dashed #cfcac2;
        border-radius: 12px;
        background: linear-gradient(140deg, #fff 0%, #f1f5f9 100%);
    }

    .result-empty-number { color: #d4d0c8; font-family: Georgia, serif; font-size: 5rem; line-height: .8; }
    .result-empty h2 { max-width: 17rem; margin: 1.2rem 0 .5rem; color: var(--ink); font-family: Georgia, serif; font-size: 1.65rem; font-weight: 500; letter-spacing: -.04em; }
    .result-empty p { max-width: 20rem; margin: 0; color: var(--muted); font-size: .88rem; line-height: 1.6; }

    .result-card {
        overflow: hidden;
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 12px;
    }

    .result-main {
        padding: 1.65rem;
        background: var(--accent);
        color: #fff;
    }
    .result-kicker { margin: 0 0 .7rem; color: #cbd5e1; font-size: .7rem; font-weight: 750; letter-spacing: .1em; text-transform: uppercase; }
    .result-value {
        margin: 0;
        color: #fff;
        font-family: Iowan Old Style, Baskerville, Georgia, serif;
        font-size: clamp(3.2rem, 6vw, 4.9rem);
        font-variant-numeric: tabular-nums;
        font-weight: 500;
        letter-spacing: -.075em;
        line-height: .9;
        text-shadow: 0 1px 0 rgba(0, 0, 0, .18);
    }
    .result-subtitle { max-width: 29rem; margin: .9rem 0 0; color: #cbd5e1; font-size: .84rem; line-height: 1.5; }

    .result-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
    }

    .result-stat { min-width: 0; padding: 1rem; border-right: 1px solid var(--line); }
    .result-stat:last-child { border-right: 0; }
    .result-stat-label { display: block; color: var(--muted); font-size: .64rem; font-weight: 750; letter-spacing: .07em; text-transform: uppercase; }
    .result-stat-value { display: block; margin-top: .38rem; color: var(--ink); font-size: .9rem; font-weight: 700; overflow-wrap: anywhere; }

    .result-insight { padding: 1.15rem 1.55rem; background: #fcfcfb; }
    .result-insight p { margin: 0; color: var(--muted); font-size: .82rem; line-height: 1.55; }

    .badge, .conf {
        display: inline-block;
        border-radius: 999px;
        font-weight: 700;
        letter-spacing: -.01em;
    }
    .badge { padding: .38rem .7rem; font-size: .8rem; }
    .conf { margin-left: .3rem; padding: .16rem .5rem; font-size: .7rem; }
    .badge-high, .conf-high { background: var(--positive-bg); color: var(--positive-ink); }
    .badge-medium, .conf-medium { background: var(--medium-bg); color: var(--medium-ink); }
    .badge-low, .conf-low { background: var(--low-bg); color: var(--low-ink); }
    .conf-na { background: var(--soft); color: var(--muted); }

    .reason-list { display: grid; gap: .5rem; margin-top: .9rem; }
    .reason-item { padding-left: .8rem; border-left: 2px solid #d5d0c7; color: var(--muted); font-size: .82rem; line-height: 1.45; }

    .lead-card {
        margin-top: 1.25rem;
        margin-bottom: .85rem;
        padding: 1.35rem;
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 12px;
        color: var(--ink);
    }
    .lead-card h3 { margin: 0; font-family: Georgia, serif; font-size: 1.35rem; font-weight: 500; letter-spacing: -.035em; }
    .lead-card p { margin: .45rem 0 0; color: var(--muted); font-size: .82rem; line-height: 1.5; }
    .lead-actions { margin-top: .2rem; }

    .stButton > button, .stFormSubmitButton > button {
        width: 100%;
        min-height: 2.85rem;
        border: 1px solid #cbd5e1 !important;
        border-radius: 7px !important;
        background: #fff !important;
        color: var(--ink) !important;
        font-size: .87rem;
        font-weight: 700;
        transition: transform .16s ease, background .16s ease, border-color .16s ease;
    }

    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
        border-color: var(--accent) !important;
        background: var(--accent) !important;
        color: #fff !important;
    }

    .stButton > button:hover, .stFormSubmitButton > button:hover { border-color: var(--accent-hover) !important; background: #f1f5f9 !important; transform: translateY(-1px); box-shadow: none !important; }
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover { background: var(--accent-hover) !important; color: #fff !important; }
    .stButton > button:focus-visible, .stFormSubmitButton > button:focus-visible {
        outline: 3px solid #0369a1 !important;
        outline-offset: 3px;
    }

    .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input, .stTextInput input {
        min-height: 2.75rem;
        border: 1px solid #cbd5e1 !important;
        border-radius: 7px !important;
        background: #fff !important;
        color: var(--ink) !important;
        box-shadow: none !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:focus-within, .stNumberInput input:focus, .stTextInput input:focus {
        border-color: #0369a1 !important;
        box-shadow: 0 0 0 3px rgba(3, 105, 161, .24) !important;
    }
    [data-testid="stWidgetLabel"] p { color: var(--ink) !important; font-size: .82rem !important; font-weight: 650 !important; }
    [data-testid="stFileUploader"] { padding: .3rem; border: 1px dashed #cbd5e1; border-radius: 8px; background: #f8fafc; }
    [data-testid="stFileUploader"] section { border: 0 !important; background: transparent !important; }
    [data-testid="stAlert"], [data-testid="stExpander"] { border: 1px solid var(--line) !important; border-radius: 8px !important; box-shadow: none !important; }
    [data-testid="stExpander"] { background: var(--paper) !important; }
    .stCaption { color: var(--muted) !important; }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            scroll-behavior: auto !important;
            transition-duration: .01ms !important;
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
        }
    }

    @media (max-width: 800px) {
        .block-container { padding: .75rem 1rem 3rem !important; }
        .topbar { margin-bottom: 2.4rem; }
        .topbar-note { display: none; }
        .hero { grid-template-columns: 1fr; gap: 1.25rem; margin-bottom: 2rem; }
        .hero h1 { font-size: clamp(2.45rem, 14vw, 4rem); }
        .trust-list { grid-template-columns: repeat(3, 1fr); min-width: 0; padding: 1rem 0 0; border-top: 1px solid var(--line); border-left: 0; }
        .workflow { grid-template-columns: 1fr; }
        .workflow-step { border-right: 0; border-bottom: 1px solid var(--line); }
        .workflow-step:last-child { border-bottom: 0; }
        .panel { padding: 1.2rem; }
        .result-grid { grid-template-columns: 1fr; }
        .result-stat { border-right: 0; border-bottom: 1px solid var(--line); }
        .result-stat:last-child { border-bottom: 0; }
    }
</style>
""",
    unsafe_allow_html=True,
)


def _safe_html(value: object) -> str:
    return escape(str(value), quote=True)


def _fmt(value: int | float | None) -> str:
    if value is None:
        return "—"
    return f"{int(value):,}".replace(",", "\u2009") + " ₽"


def _normalize_phone(value: str) -> str | None:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith(("7", "8")):
        return "+7" + digits[1:]
    if len(digits) == 10:
        return "+7" + digits
    return None


def _validate_photos(photos) -> str | None:
    if not photos:
        return "Загрузите хотя бы одну фотографию изделия."
    if len(photos) > 4:
        return "Можно загрузить не более четырёх фотографий."
    if any(photo.size > 8 * 1024 * 1024 for photo in photos):
        return "Размер каждого файла не должен превышать 8 МБ."
    return None


def _confidence_badge(confidence: str) -> str:
    mapping = {
        "высокая": ("conf-high", "высокая точность"),
        "средняя": ("conf-medium", "средняя точность"),
        "низкая": ("conf-low", "низкая точность"),
    }
    css_class, label = mapping.get(confidence, ("conf-na", "нет данных"))
    return f'<span class="conf {css_class}">{label}</span>'


BRANCHES = [
    {"name": "СКС Ломбард — Центральный", "address": "Революционная ул., 52"},
    {"name": "СКС Ломбард — Октябрьский", "address": "просп. Октября, 160"},
    {"name": "СКС Ломбард — Зелёная Роща", "address": "ул. Степана Кувыкина, 1Г"},
    {"name": "СКС Ломбард — Дема", "address": "ул. Правды, 20"},
]


@st.dialog("Перед началом")
def show_disclaimer():
    st.markdown("### Важная информация")
    st.write("Расчёт является предварительным и основан на фотографиях и указанных данных.")
    st.markdown(
        "- Оценка веса по фотографии приблизительна.\n"
        "- Окончательное решение и сумма определяются товароведом после осмотра.\n"
        "- Условия займа и выкупа могут отличаться от расчёта."
    )
    if st.button("Понятно, продолжить", type="primary", use_container_width=True):
        st.session_state["disclaimer_accepted"] = True
        st.rerun()


def _create_lead(name: str, phone: str, branch: dict | None = None) -> dict:
    analysis = st.session_state.get("last_analysis", {})
    if branch:
        analysis = {**analysis, "branch_name": branch["name"], "branch_address": branch["address"]}
    return create_deal(
        client_name=name,
        client_phone=phone,
        analysis=analysis,
        price=st.session_state.get("last_price", {}),
        prob=st.session_state.get("last_prob", {}),
        photos_count=st.session_state.get("last_photos_count", 0),
    )


def _store_lead_result(result: dict, lead_type: str, branch_name: str | None = None) -> None:
    st.session_state["deal_created"] = True
    st.session_state["deal_id"] = result["deal_id"]
    st.session_state["deal_type"] = lead_type
    st.session_state["deal_mode"] = result["mode"]
    if branch_name:
        st.session_state["deal_branch"] = branch_name
    st.session_state["open_dialog"] = None
    st.rerun()


@st.dialog("Заказать обратный звонок")
def dialog_callback():
    st.caption("Оставьте контакт — специалист свяжется с вами в рабочее время.")
    name = st.text_input("Ваше имя *", placeholder="Иван Иванов", key="callback_name")
    phone = st.text_input("Телефон *", placeholder="+7 (999) 123-45-67", key="callback_phone")
    consent = st.checkbox("Согласен на обработку контактных данных *", key="callback_consent")

    submit_col, cancel_col = st.columns(2)
    with submit_col:
        submitted = st.button("Отправить", type="primary", use_container_width=True)
    with cancel_col:
        cancelled = st.button("Отмена", use_container_width=True)

    if cancelled:
        st.session_state["open_dialog"] = None
        st.rerun()
    if submitted:
        normalized_phone = _normalize_phone(phone)
        if not name.strip():
            st.error("Укажите имя.")
        elif not normalized_phone:
            st.error("Укажите номер в формате +7 (999) 123-45-67.")
        elif not consent:
            st.error("Подтвердите согласие на обработку контактных данных.")
        else:
            result = _create_lead(name.strip(), normalized_phone)
            if result["success"]:
                _store_lead_result(result, "callback")
            else:
                st.error(result["message"])


@st.dialog("Выбрать отделение", width="large")
def dialog_branch():
    st.caption("Выберите удобное отделение и оставьте контакт для подтверждения визита.")
    choice = st.radio(
        "Отделение",
        options=range(len(BRANCHES)),
        format_func=lambda index: f"{BRANCHES[index]['name']} · {BRANCHES[index]['address']}",
        label_visibility="collapsed",
    )
    name = st.text_input("Ваше имя *", placeholder="Иван Иванов", key="branch_name")
    phone = st.text_input("Телефон *", placeholder="+7 (999) 123-45-67", key="branch_phone")
    consent = st.checkbox("Согласен на обработку контактных данных *", key="branch_consent")

    submit_col, cancel_col = st.columns(2)
    with submit_col:
        submitted = st.button("Записаться", type="primary", use_container_width=True)
    with cancel_col:
        cancelled = st.button("Отмена", use_container_width=True)

    if cancelled:
        st.session_state["open_dialog"] = None
        st.rerun()
    if submitted:
        normalized_phone = _normalize_phone(phone)
        if not name.strip():
            st.error("Укажите имя.")
        elif not normalized_phone:
            st.error("Укажите номер в формате +7 (999) 123-45-67.")
        elif not consent:
            st.error("Подтвердите согласие на обработку контактных данных.")
        else:
            branch = BRANCHES[choice]
            result = _create_lead(name.strip(), normalized_phone, branch)
            if result["success"]:
                _store_lead_result(result, "branch", branch["name"])
            else:
                st.error(result["message"])


if not st.session_state.get("disclaimer_accepted", False):
    show_disclaimer()
elif st.session_state.get("open_dialog") == "callback":
    dialog_callback()
elif st.session_state.get("open_dialog") == "branch":
    dialog_branch()

st.markdown(
    """
<header class="topbar">
    <div class="wordmark"><span class="wordmark-mark" aria-hidden="true"><svg viewBox="0 0 24 24" focusable="false"><path d="M12 2.5 21.5 12 12 21.5 2.5 12 12 2.5Zm0 4.1L6.6 12l5.4 5.4 5.4-5.4L12 6.6Z"/></svg></span>СКС ЛОМБАРД</div>
    <div class="topbar-note">Уфа · Предварительная онлайн-оценка</div>
</header>
<section class="hero">
    <div>
        <p class="eyebrow">Оценка по фотографии</p>
        <h1>Узнайте сумму<br><em>до визита</em> в ломбард</h1>
        <p class="hero-copy">Загрузите фотографии украшения. Мы оценим его состояние, рассчитаем ориентировочную сумму займа и поможем выбрать следующий шаг.</p>
    </div>
    <aside class="trust-list" aria-label="Преимущества сервиса">
        <div class="trust-item"><strong>До 4 фотографий</strong>для более точной оценки</div>
        <div class="trust-item"><strong>Расчёт за минуту</strong>без визита в отделение</div>
        <div class="trust-item"><strong>Без обязательств</strong>итог решает товаровед</div>
    </aside>
</section>
<div class="workflow" aria-label="Как это работает">
    <div class="workflow-step"><span class="step-index">1</span>Добавьте фотографии</div>
    <div class="workflow-step"><span class="step-index">2</span>Получите расчёт</div>
    <div class="workflow-step"><span class="step-index">3</span>Выберите удобный способ связи</div>
</div>
""",
    unsafe_allow_html=True,
)

if not settings.ai_enabled:
    st.info("Демонстрационный режим: AI-анализ станет доступен после подключения Yandex Cloud AI Studio.")

form_column, result_column = st.columns([1.04, 0.96], gap="large")

with form_column:
    st.markdown(
        """
<section class="panel">
    <div class="panel-heading">
        <div><h2 class="panel-title">Расскажите об украшении</h2><p class="panel-caption">Чем точнее исходные данные, тем полезнее предварительный расчёт.</p></div>
        <span class="panel-index">01 / 02</span>
    </div>
""",
        unsafe_allow_html=True,
    )
    with st.form("jewelry_form", clear_on_submit=False):
        st.markdown('<div class="form-section-label">Фотографии</div>', unsafe_allow_html=True)
        photos = st.file_uploader(
            "Фотографии изделия *",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help="От 1 до 4 фотографий, до 8 МБ каждая. Покажите изделие целиком и крупные детали.",
        )
        st.markdown('<div class="form-section-label">Характеристики</div>', unsafe_allow_html=True)
        left_field, right_field = st.columns(2)
        with left_field:
            item_type = st.selectbox("Тип изделия", ["Кольцо", "Серьги", "Браслет", "Кулон", "Цепь", "Колье"])
            condition = st.selectbox("Визуальное состояние", ["Как новое", "Среднее", "Плохое"])
        with right_field:
            sample = st.selectbox("Проба металла", ["375", "585", "750"], index=1)
            weight = st.number_input("Вес, г — если известен", min_value=0.0, step=0.1, help="Если вес неизвестен, оставьте 0 — сервис попробует оценить его по фото.")
        has_inserts = st.radio("Есть вставки или камни?", ["Нет", "Да"], horizontal=True) == "Да"
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Рассчитать предварительную сумму", type="primary", use_container_width=True)
    photo_error = _validate_photos(photos) if submitted else None
    if photo_error:
        st.error(f"Не удалось начать расчёт: {photo_error} Исправьте это и попробуйте снова.")
    st.markdown("</section>", unsafe_allow_html=True)
    st.caption("Отправляя фотографии, вы соглашаетесь с предварительным характером оценки. Финальное решение принимает специалист после осмотра.")

with result_column:
    if photo_error:
        st.markdown(
            """
<aside class="result-empty">
    <div class="result-empty-number">!</div>
    <h2>Добавьте фотографии для расчёта</h2>
    <p>После исправления данных здесь появится предварительная оценка и следующие действия.</p>
</aside>
""",
            unsafe_allow_html=True,
        )
    elif not submitted and "last_analysis" not in st.session_state:
        st.markdown(
            """
<aside class="result-empty">
    <div class="result-empty-number">01</div>
    <h2>Ваш расчёт появится здесь</h2>
    <p>Добавьте фотографии и характеристики изделия. Сервис покажет ориентировочную сумму и важные детали оценки.</p>
</aside>
""",
            unsafe_allow_html=True,
        )
    else:
        if submitted:
            for key in ("deal_created", "deal_id", "deal_type", "deal_mode", "deal_branch", "open_dialog"):
                st.session_state.pop(key, None)

            form_data = {
                "type": item_type,
                "sample": sample,
                "has_inserts": has_inserts,
                "condition": condition,
                "weight_g": weight if weight > 0 else None,
            }
            image_bytes = [photo.getvalue() for photo in photos]
            with st.spinner("Проверяем фотографии и считаем сумму…"):
                analysis = analyze_jewelry(image_bytes, form_data)

            final_weight = weight if weight > 0 else (analysis.get("estimated_weight_g") or 0)
            price = calculate_price(
                {
                    "item_type": analysis["type"],
                    "fineness": sample,
                    "has_inserts": analysis["has_inserts"],
                    "condition": analysis["condition"],
                    "weight": final_weight,
                }
            )
            probability = acceptance_probability(
                {
                    "condition": analysis["condition"],
                    "has_inserts": analysis["has_inserts"],
                    "weight": final_weight,
                    "has_defects": analysis.get("has_defects", False),
                    "insert_damage": analysis.get("insert_damage", False),
                    "defects_description": analysis.get("defects_description", ""),
                    "defect_severity": analysis.get("defect_severity", "нет"),
                    "repairable": analysis.get("repairable", True),
                }
            )
            st.session_state.update(
                {
                    "last_analysis": analysis,
                    "last_price": price,
                    "last_prob": probability,
                    "last_photos_count": len(image_bytes),
                    "last_weight_is_est": weight <= 0,
                    "last_final_weight": final_weight,
                    "last_photos_bytes": image_bytes,
                }
            )

        analysis = st.session_state["last_analysis"]
        price = st.session_state["last_price"]
        probability = st.session_state["last_prob"]
        final_weight = st.session_state.get("last_final_weight", 0)
        weight_is_estimated = st.session_state.get("last_weight_is_est", False)
        photos_bytes = st.session_state.get("last_photos_bytes", [])
        score = probability["probability"]
        badge_class = "badge-high" if score >= 80 else "badge-medium" if score >= 50 else "badge-low"
        source_label = "Анализ фотографий" if analysis.get("analysis_source") == "ai" else "Расчёт по анкете"
        weight_label = "оценка по фото" if weight_is_estimated else "указано вами"
        buyout = (
            f"{_fmt(price['buyout_amount'])} + {price['daily_interest_rate']:g}% / день"
            if price["buyout_amount"] is not None else "Нужен вес"
        )

        st.markdown(
            f"""
<section class="result-card">
    <div class="result-main">
        <p class="result-kicker">Предварительная сумма займа · {source_label}</p>
        <p class="result-value">{_fmt(price['loan_amount'])}</p>
        <p class="result-subtitle">Окончательная сумма зависит от осмотра товара и условий в отделении.</p>
    </div>
    <div class="result-grid">
        <div class="result-stat"><span class="result-stat-label">Вес · {weight_label}</span><span class="result-stat-value">{final_weight:g} г</span></div>
        <div class="result-stat"><span class="result-stat-label">Цена за грамм</span><span class="result-stat-value">{price['price_per_gram']:,} ₽</span></div>
        <div class="result-stat"><span class="result-stat-label">Выкуп</span><span class="result-stat-value">{buyout}</span></div>
    </div>
    <div class="result-insight"><p>Вероятность рассмотрения: <span class="badge {badge_class}">{_safe_html(probability['verdict'])} · {score}%</span></p></div>
</section>
""",
            unsafe_allow_html=True,
        )

        if analysis.get("analysis_source") == "form":
            st.warning("AI-анализ временно недоступен: показан расчёт только по данным анкеты. Для оценки по фотографии повторите попытку позже.")
        elif weight_is_estimated and final_weight:
            minimum, maximum = analysis.get("weight_min_g"), analysis.get("weight_max_g")
            range_text = f" Диапазон: {minimum:g}–{maximum:g} г." if minimum and maximum else ""
            st.markdown(
                f'<p class="panel-caption">Вес определён по фотографии · '
                f'{_confidence_badge(analysis.get("weight_confidence", "низкая"))}{range_text}</p>',
                unsafe_allow_html=True,
            )
        elif weight_is_estimated:
            st.warning("Не удалось оценить вес по фотографии. Укажите фактический вес, чтобы получить сумму.")

        if probability["reasons"]:
            with st.expander("Что повлияло на расчёт", expanded=False):
                st.markdown('<div class="reason-list">', unsafe_allow_html=True)
                for reason in probability["reasons"]:
                    st.markdown(f'<div class="reason-item">{_safe_html(reason)}</div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Детали оценки", expanded=False):
            info_left, info_right = st.columns(2)
            info_left.write(f"**Тип:** {analysis['type']}")
            info_left.write(f"**Состояние:** {analysis['condition']}")
            info_left.write(f"**Вставки:** {'Да' if analysis['has_inserts'] else 'Нет'}")
            info_right.write(f"**Дефекты:** {'Есть' if analysis['has_defects'] else 'Не выявлены'}")
            info_right.write(f"**Серьёзность:** {analysis.get('defect_severity', '—')}")
            info_right.write(f"**Ремонтопригодно:** {'Да' if analysis.get('repairable', True) else 'Нет'}")
            st.write(f"**Комментарий:** {analysis.get('visual_notes', '—')}")
            st.write(f"**Обоснование веса:** {analysis.get('weight_reasoning', '—')}")

        if photos_bytes:
            with st.expander("Загруженные фотографии", expanded=False):
                image_columns = st.columns(min(len(photos_bytes), 4))
                for index, image in enumerate(photos_bytes):
                    image_columns[index % len(image_columns)].image(image, use_container_width=True)

        st.markdown(
            """
<section class="lead-card">
    <h3>Продолжим в удобном формате?</h3>
    <p>Выберите отделение для визита или оставьте номер — специалист поможет уточнить условия.</p>
</section>
""",
            unsafe_allow_html=True,
        )

        if st.session_state.get("deal_created"):
            deal_type = st.session_state.get("deal_type")
            deal_id = st.session_state.get("deal_id")
            if deal_type == "branch":
                st.success(f"Заявка #{deal_id} создана. Ждём вас: {st.session_state.get('deal_branch')}.")
            else:
                st.success(f"Заявка #{deal_id} создана. Специалист свяжется с вами в рабочее время.")
            if st.session_state.get("deal_mode") == "demo":
                st.info("Демо-режим: обращение показано в интерфейсе и не было отправлено в CRM.")
        else:
            visit_button, callback_button = st.columns(2)
            with visit_button:
                if st.button("Выбрать отделение", key="choose_branch", use_container_width=True):
                    st.session_state["open_dialog"] = "branch"
                    st.rerun()
            with callback_button:
                if st.button("Заказать звонок", key="request_callback", use_container_width=True):
                    st.session_state["open_dialog"] = "callback"
                    st.rerun()
""