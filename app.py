# app.py
import streamlit as st
from analyzer import analyze_jewelry
from pricing  import calculate_price, acceptance_probability
from bitrix   import create_deal

st.set_page_config(
    page_title="СКС Ломбард — Оценка ювелирных изделий",
    page_icon="https://sks-lombard.ru/local/templates/sks-lombard/assets/images/favicon/icon1.ico",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    /* Сброс стилей Streamlit */
    .stApp {
        background: #ffffff !important;
    }
    
    /* Переменные */
    :root {
        --red: #e30613;
        --red-dark: #b00410;
        --bg: #ffffff;
        --bg-soft: #fafafa;
        --bg-card: #ffffff;
        --border: #e5e7eb;
        --text: #1f2937;
        --text-muted: #6b7280;
    }
    
    /* Скрываем меню и футер */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    /* Основной контейнер */
    .block-container {
        padding-top: 1.2rem !important;
        max-width: 1150px !important;
    }
    
    /* Бренд-бар */
    .brand-bar {
        background: #ffffff !important;
        border: 1px solid var(--border) !important;
        border-bottom: 3px solid var(--red) !important;
        border-radius: 14px !important;
        padding: 1.4rem 1.8rem !important;
        margin-bottom: 1.4rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 1.1rem !important;
        box-shadow: 0 4px 18px rgba(0,0,0,.05) !important;
    }
    
    .brand-logo {
        width: 58px !important;
        height: 58px !important;
        min-width: 58px !important;
        border-radius: 12px !important;
        background: var(--red) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 800 !important;
        font-size: 1.25rem !important;
        color: #ffffff !important;
        letter-spacing: 1px !important;
        box-shadow: 0 2px 8px rgba(227,6,19,.3) !important;
    }
    
    .brand-text h1 {
        color: var(--text) !important;
        font-size: 1.55rem !important;
        margin: 0 !important;
        font-weight: 800 !important;
    }
    
    .brand-text .sub {
        color: var(--text-muted) !important;
        font-size: .92rem !important;
        margin-top: .15rem !important;
    }
    
    /* Карточки */
    .card {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-top: 3px solid var(--red) !important;
        border-radius: 12px !important;
        padding: 1.5rem 1.5rem 1.2rem !important;
        box-shadow: 0 2px 10px rgba(0,0,0,.04) !important;
        margin-bottom: 1.2rem !important;
    }
    
    .card h3 {
        font-size: 1.12rem !important;
        margin-top: 0 !important;
        color: var(--text) !important;
        border-left: 4px solid var(--red) !important;
        padding-left: .65rem !important;
        margin-bottom: 1.1rem !important;
        font-weight: 700 !important;
    }
    
    /* Метрики */
    .metric-box {
        background: var(--bg-soft) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 1rem 1.2rem !important;
        text-align: center !important;
        height: 100% !important;
    }
    
    .metric-box .label {
        font-size: .78rem !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: .6px !important;
    }
    
    .metric-box .value {
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        color: var(--text) !important;
        margin-top: .35rem !important;
    }
    
    /* Бейджи */
    .badge {
        display: inline-block !important;
        padding: .35rem .9rem !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: .95rem !important;
    }
    
    .badge-high { background: #e3f5e8 !important; color: #1b7a3d !important; }
    .badge-medium { background: #fff4e0 !important; color: #a76a00 !important; }
    .badge-low { background: #fde8e8 !important; color: #b42318 !important; }
    
    .conf {
        display: inline-block !important;
        padding: .15rem .6rem !important;
        border-radius: 14px !important;
        font-size: .78rem !important;
        font-weight: 600 !important;
        margin-left: .4rem !important;
    }
    
    .conf-high { background: #e3f5e8 !important; color: #1b7a3d !important; }
    .conf-medium { background: #fff4e0 !important; color: #a76a00 !important; }
    .conf-low { background: #fde8e8 !important; color: #b42318 !important; }
    .conf-na { background: #eceff3 !important; color: #6b7280 !important; }
    
    /* Кнопки - ИСПРАВЛЕНО */
    .stButton > button {
        background-color: var(--red) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.4rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: var(--red-dark) !important;
        color: #ffffff !important;
        box-shadow: 0 3px 12px rgba(227,6,19,.3) !important;
        border: none !important;
    }
    
    /* Кнопки в формах */
    .stFormSubmitButton > button {
        background-color: var(--red) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.4rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    
    .stFormSubmitButton > button:hover {
        background-color: var(--red-dark) !important;
        color: #ffffff !important;
        box-shadow: 0 3px 12px rgba(227,6,19,.3) !important;
        border: none !important;
    }
    
    /* Дополнительные стили */
    .weight-note {
        font-size: .85rem !important;
        color: var(--text-muted) !important;
        margin-top: .4rem !important;
    }
    
    .convert-section {
        border-top: 2px solid var(--border) !important;
        margin-top: 1.4rem !important;
        padding-top: 1.2rem !important;
    }
    
    .reason-item {
        padding: 0.3rem 0;
        color: var(--text-muted);
        font-size: 0.9rem;
    }
    
    /* Переопределение стилей Streamlit для selectbox, input и radio */
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border-color: var(--border) !important;
    }
    
    .stNumberInput input {
        border-radius: 8px !important;
        border-color: var(--border) !important;
    }
    
    /* Адаптивный текст */
    .responsive-value {
        font-size: clamp(12px, 2.5vw, 16px) !important;
        word-break: break-word !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Шапка ──
st.markdown("""
<div class="brand-bar">
    <img src="https://sks-lombard.ru/local/templates/sks-lombard/assets/images/favicon/icon1.ico"
         class="brand-logo" alt="СКС">
    <div class="brand-text">
        <h1>СКС Ломбард</h1>
        <div class="sub">Предварительная оценка ювелирных изделий по фотографиям</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Вспомогательные функции ──
def _conf_badge(conf: str) -> str:
    mapping = {
        "высокая": ("conf-high",   "высокая точность"),
        "средняя": ("conf-medium", "средняя точность"),
        "низкая":  ("conf-low",    "низкая точность"),
    }
    cls, label = mapping.get(conf, ("conf-na", "нет данных"))
    return f'<span class="conf {cls}">{label}</span>'


def _fmt(value) -> str:
    if value is None:
        return "—"
    return f"{int(value):,}".replace(",", "\u2009") + " ₽"


# ── Константы ──
BRANCHES = [
    {"name": "СКС Ломбард — Центральный",   "address": "Революционная ул., 52",       "city": "Уфа"},
    {"name": "СКС Ломбард — Октябрьский",       "address": "просп. Октября, 160",        "city": "Уфа"},
    {"name": "СКС Ломбард — Зелёная Роща",          "address": "ул. Степана Кувыкина, 1Г",      "city": "Уфа"},
    {"name": "СКС Ломбард — Дема",       "address": "ул. Правды, 20", "city": "Уфа"},
]

@st.dialog("⚠️ Важная информация")
def show_disclaimer():
    st.markdown("""
    **Расчёт является предварительным** и выполнен на основании фотографий
    и предоставленных данных.

    - Вес, определённый по фотографии, носит **оценочный характер**.
    - Окончательная оценка определяется **специалистом** после очного
      осмотра в подразделении компании.
    - Итоговые суммы займа и выкупа могут отличаться от предварительного расчёта.
    """)
    if st.button("Понятно, продолжить", type="primary"):
        st.session_state["disclaimer_accepted"] = True
        st.rerun()


@st.dialog("Заказать обратный звонок")
def dialog_callback():
    analysis     = st.session_state.get("last_analysis", {})
    price        = st.session_state.get("last_price", {})
    prob         = st.session_state.get("last_prob", {})
    photos_count = st.session_state.get("last_photos_count", 0)

    st.markdown("Оставьте контакты — специалист свяжется с вами в рабочее время.")
    name  = st.text_input("ФИО *",           placeholder="Иванов Иван Иванович")
    phone = st.text_input("Номер телефона *", placeholder="+7 (___) ___-__-__")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Отправить заявку", type="primary"):
            if not name.strip():
                st.error("Пожалуйста, укажите ФИО.")
            elif not phone.strip():
                st.error("Пожалуйста, укажите номер телефона.")
            else:
                result = create_deal(
                    client_name=name.strip(),
                    client_phone=phone.strip(),
                    analysis=analysis,
                    price=price,
                    prob=prob,
                    photos_count=photos_count,
                )
                if result["success"]:
                    # Сохраняем результат и закрываем диалог
                    st.session_state["deal_created"]  = True
                    st.session_state["deal_id"]       = result["deal_id"]
                    st.session_state["deal_type"]     = "callback"
                    st.session_state["open_dialog"]   = None   # закрыть диалог
                    st.rerun()
                else:
                    st.error("Ошибка при создании заявки. Попробуйте позже.")
    with col2:
        if st.button("Отмена"):
            st.session_state["open_dialog"] = None
            st.rerun()


@st.dialog("Выбрать подразделение", width="large")
def dialog_branch():
    analysis     = st.session_state.get("last_analysis", {})
    price        = st.session_state.get("last_price", {})
    prob         = st.session_state.get("last_prob", {})
    photos_count = st.session_state.get("last_photos_count", 0)

    st.markdown("Выберите удобное подразделение и оставьте контакты.")

    branch_names = [f"{b['name']} — {b['address']}" for b in BRANCHES]
    selected_idx = st.radio(
        "Подразделения",
        range(len(branch_names)),
        format_func=lambda i: branch_names[i],
    )

    st.markdown("---")
    name  = st.text_input("ФИО *",           placeholder="Иванов Иван Иванович")
    phone = st.text_input("Номер телефона *", placeholder="+7 (___) ___-__-__")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Посетить это подразделение", type="primary"):
            if not name.strip():
                st.error("Пожалуйста, укажите ФИО.")
            elif not phone.strip():
                st.error("Пожалуйста, укажите номер телефона.")
            else:
                branch = BRANCHES[selected_idx]
                enriched_analysis = {
                    **analysis,
                    "branch_name":    branch["name"],
                    "branch_address": branch["address"],
                }
                result = create_deal(
                    client_name=name.strip(),
                    client_phone=phone.strip(),
                    analysis=enriched_analysis,
                    price=price,
                    prob=prob,
                    photos_count=photos_count,
                )
                if result["success"]:
                    st.session_state["deal_created"]  = True
                    st.session_state["deal_id"]       = result["deal_id"]
                    st.session_state["deal_type"]     = "branch"
                    st.session_state["deal_branch"]   = branch["name"]
                    st.session_state["open_dialog"]   = None   # закрыть диалог
                    st.rerun()
                else:
                    st.error("Ошибка при создании заявки. Попробуйте позже.")
    with col2:
        if st.button("Отмена"):
            st.session_state["open_dialog"] = None
            st.rerun()


if not st.session_state.get("disclaimer_accepted", False):
    show_disclaimer()
elif st.session_state.get("open_dialog") == "callback":
    dialog_callback()
elif st.session_state.get("open_dialog") == "branch":
    dialog_branch()


# ── Основной интерфейс ──
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="card"><h3>Данные изделия</h3>', unsafe_allow_html=True)
    with st.form("jewelry_form"):
        photos = st.file_uploader(
            "Фотографии изделия",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help="Загрузите 1–4 фотографии при хорошем освещении.",
        )
        c1, c2 = st.columns(2)
        with c1:
            item_type = st.selectbox("Тип изделия",
                                     ["Кольцо","Серьги","Браслет","Кулон","Цепь","Колье"])
            sample    = st.selectbox("Проба металла", ["375","585","750"])
        with c2:
            condition = st.selectbox("Состояние", ["Как новое","Среднее","Плохое"])
            weight    = st.number_input(
                "Вес изделия, г (если известен)",
                min_value=0.0, step=0.1,
                help="Если вес неизвестен — оставьте 0, ИИ оценит его по фото.",
            )
        has_inserts = st.radio("Наличие вставок", ["Нет","Да"], horizontal=True) == "Да"
        submitted   = st.form_submit_button("Оценить изделие")
    st.markdown("</div>", unsafe_allow_html=True)


with right:
    if not submitted and "last_analysis" not in st.session_state:
        st.markdown(
            '<div class="card"><h3>Результат оценки</h3>'
            '<p style="color:#6b7280;">Заполните данные изделия и нажмите '
            '«Оценить изделие», чтобы получить предварительный расчёт.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        # При новой отправке формы — пересчитываем и сбрасываем сделку
        if submitted:
            st.session_state.pop("deal_created", None)
            st.session_state.pop("deal_id",      None)
            st.session_state.pop("deal_type",    None)
            st.session_state.pop("deal_branch",  None)
            st.session_state.pop("open_dialog",  None)

            form_data = {
                "type":        item_type,
                "sample":      sample,
                "has_inserts": has_inserts,
                "condition":   condition,
                "weight_g":    weight if weight > 0 else None,
            }
            img_bytes = [p.read() for p in photos] if photos else []

            with st.spinner("Анализируем изделие..."):
                analysis = analyze_jewelry(img_bytes, form_data)

            final_weight        = weight if weight > 0 else (analysis.get("estimated_weight_g") or 0)
            weight_is_estimated = weight <= 0

            price = calculate_price({
                "item_type":   analysis["type"],
                "fineness":    sample,
                "has_inserts": analysis["has_inserts"],
                "condition":   analysis["condition"],
                "weight":      final_weight,
            })
            prob = acceptance_probability({
                "condition":           analysis["condition"],
                "has_inserts":         analysis["has_inserts"],
                "weight":              final_weight,
                "has_defects":         analysis.get("has_defects", False),
                "insert_damage":       analysis.get("insert_damage", False),
                "defects_description": analysis.get("defects_description", ""),
                "defect_severity":     analysis.get("defect_severity", "нет"),
                "repairable":          analysis.get("repairable", True),
            })

            # Сохраняем всё в session_state
            st.session_state["last_analysis"]        = analysis
            st.session_state["last_price"]           = price
            st.session_state["last_prob"]            = prob
            st.session_state["last_photos_count"]    = len(img_bytes)
            st.session_state["last_weight_is_est"]   = weight_is_estimated
            st.session_state["last_final_weight"]    = final_weight
            st.session_state["last_photos_objects"]  = photos  # для отображения

        # Читаем из session_state (работает и после rerun без повторной отправки)
        analysis            = st.session_state["last_analysis"]
        price               = st.session_state["last_price"]
        prob                = st.session_state["last_prob"]
        weight_is_estimated = st.session_state.get("last_weight_is_est", False)
        final_weight        = st.session_state.get("last_final_weight", 0)
        photos_objects      = st.session_state.get("last_photos_objects", [])

        # ── Карточка результата ──
        st.markdown('<div class="card"><h3>Результат оценки</h3>', unsafe_allow_html=True)

        weight_display = f"{final_weight:g} г" if final_weight else "—"
        weight_label   = "Вес (оценка по фото)" if weight_is_estimated else "Вес изделия"
        ppg            = f"{price['price_per_gram']:,}".replace(",", "\u2009")
        buyout_label = f"{price['buyout_amount']} + 0,29%/день"

        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(
            f'<div class="metric-box"><div class="label">{weight_label}</div>'
            f'<div class="value">{weight_display}</div></div>',
            unsafe_allow_html=True,
        )
        m2.markdown(
            f'<div class="metric-box"><div class="label">Цена за грамм</div>'
            f'<div class="value">{ppg} ₽</div></div>',
            unsafe_allow_html=True,
        )
        m3.markdown(
            f'<div class="metric-box"><div class="label">Сумма займа</div>'
            f'<div class="value">{_fmt(price["loan_amount"])}</div></div>',
            unsafe_allow_html=True,
        )
        m4.markdown(
            f'<div class="metric-box"><div class="label">Сумма выкупа</div>'
            f'<div class="value" style="font-size:1rem; word-break:break-word; hyphens:auto;">{buyout_label}</div></div>',
            unsafe_allow_html=True,
        )

        if price["loan_amount"] is not None:
            st.markdown(
                '<p style="font-size:.8rem;color:#888;margin-top:.5rem;">'
                '* Сумма займа — средства, выдаваемые клиенту. '
                'Сумма выкупа — сумма для возврата изделия (займ + проценты). '
                'Точные условия уточняйте у специалиста.</p>',
                unsafe_allow_html=True,
            )

        if weight_is_estimated and final_weight:
            conf    = analysis.get("weight_confidence", "низкая")
            w_min   = analysis.get("weight_min_g")
            w_max   = analysis.get("weight_max_g")
            rng_txt = f" Диапазон: {w_min:g}–{w_max:g} г." if w_min and w_max else ""
            st.markdown(
                f'<div class="weight-note"> Вес определён по фотографии '
                f'{_conf_badge(conf)}.{rng_txt} '
                f'{analysis.get("weight_reasoning", "")}</div>',
                unsafe_allow_html=True,
            )

        score     = prob["probability"]
        badge_cls = "badge-high" if score >= 80 else ("badge-medium" if score >= 50 else "badge-low")
        st.markdown(
            f'<p style="margin-top:1.2rem;">Вероятность принятия: '
            f'<span class="badge {badge_cls}">{prob["verdict"]} — {score}%</span></p>',
            unsafe_allow_html=True,
        )

        if prob["reasons"]:
            st.markdown("**Замечания:**")
            for r in prob["reasons"]:
                st.markdown(f'<div class="reason-item">{r}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Подробности анализа ИИ"):
            a1, a2 = st.columns(2)
            a1.write(f"**Тип изделия:** {analysis['type']}")
            a1.write(f"**Состояние:** {analysis['condition']}")
            a1.write(f"**Вставки:** {'Да' if analysis['has_inserts'] else 'Нет'}")
            a2.write(f"**Дефекты:** {'Да' if analysis['has_defects'] else 'Нет'}")
            a2.write(f"**Повреждение вставок:** {'Да' if analysis['insert_damage'] else 'Нет'}")
            a2.write(f"**Серьёзность дефектов:** {analysis.get('defect_severity','—')}")
            a2.write(f"**Ремонтопригодно:** {'Да' if analysis.get('repairable', True) else 'Нет'}")
            st.write(f"**Описание дефектов:** {analysis['defects_description']}")
            st.write(f"**Визуальные заметки:** {analysis['visual_notes']}")
            st.markdown("---")
            st.markdown("**Оценка веса**")
            w1, w2 = st.columns(2)
            w1.write(f"**Источник:** {analysis.get('weight_source','—')}")
            w1.write(f"**Оценочный вес:** {analysis.get('estimated_weight_g') or '—'} г")
            w2.write(f"**Диапазон:** {analysis.get('weight_min_g') or '—'}–{analysis.get('weight_max_g') or '—'} г")
            w2.write(f"**Уверенность:** {analysis.get('weight_confidence','—')}")
            st.write(f"**Обоснование веса:** {analysis.get('weight_reasoning','—')}")

        if photos_objects:
            with st.expander("Загруженные фотографии"):
                cols = st.columns(min(len(photos_objects), 4))
                for i, p in enumerate(photos_objects):
                    cols[i % len(cols)].image(p)

        if weight_is_estimated:
            if final_weight:
                st.warning(
                    "Вес рассчитан автоматически по фотографии и является "
                    "приблизительным. Для точной суммы укажите фактический вес."
                )
            else:
                st.error(
                    "Не удалось оценить вес по фотографии. "
                    "Укажите вес вручную для расчёта стоимости."
                )

        st.caption("Окончательная оценка — после очного осмотра специалистом.")

        # ── Конвертация в обращение ──
        st.markdown('<div class="convert-section">', unsafe_allow_html=True)
        st.markdown("### Оформить обращение")
        st.markdown(
            "Готовы прийти в ломбард или хотите получить консультацию? "
            "Выберите удобный способ — специалист свяжется с вами."
        )

        if st.session_state.get("deal_created"):
            deal_type   = st.session_state.get("deal_type", "")
            deal_branch = st.session_state.get("deal_branch", "")
            deal_id     = st.session_state.get("deal_id", "")
            if deal_type == "branch":
                st.success(
                    f"Заявка #{deal_id} создана! Ждём вас: **{deal_branch}**. "
                    f"Специалист может связаться с вами для подтверждения."
                )
            else:
                st.success(
                    f"Заявка #{deal_id} создана! Специалист свяжется с вами "
                    f"в ближайшее рабочее время."
                )
        else:
            btn1, btn2 = st.columns(2)
            with btn1:
                # Кнопка только выставляет флаг — диалог откроется при следующем rerun
                if st.button("Выбрать подразделение", key="btn_branch"):
                    st.session_state["open_dialog"] = "branch"
                    st.rerun()
            with btn2:
                if st.button("Заказать обратный звонок", key="btn_callback"):
                    st.session_state["open_dialog"] = "callback"
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)