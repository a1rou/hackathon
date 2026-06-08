import streamlit as st
from analyzer import analyze_jewelry
from pricing import calculate_price, acceptance_probability

st.set_page_config(
    page_title="СКС Ломбард — Оценка ювелирных изделий",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* ===== Фирменная палитра СКС Ломбард (светлый + красный) ===== */
    :root {
        --red:         #e30613;   /* фирменный красный */
        --red-dark:    #b00410;
        --red-light:   #ff4b57;
        --bg:          #ffffff;
        --bg-soft:     #fbf2ee;   /* светло-бежевый/розоватый */
        --bg-card:     #ffffff;
        --border:      #ececec;
        --text:        #2b2b2b;
        --text-muted:  #888888;
    }

    #MainMenu, footer {visibility: hidden;}

    .stApp {
        background: var(--bg);
    }

    .block-container {
        padding-top: 1.2rem;
        max-width: 1150px;
    }

    /* ===== Шапка-бренд ===== */
    .brand-bar {
        background: #ffffff;
        border: 1px solid var(--border);
        border-bottom: 3px solid var(--red);
        border-radius: 14px;
        padding: 1.4rem 1.8rem;
        margin-bottom: 1.4rem;
        display: flex;
        align-items: center;
        gap: 1.1rem;
        box-shadow: 0 4px 18px rgba(0,0,0,0.05);
    }
    .brand-logo {
        width: 58px;
        height: 58px;
        min-width: 58px;
        border-radius: 12px;
        background: var(--red);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.25rem;
        color: #fff;
        letter-spacing: 1px;
        box-shadow: 0 2px 8px rgba(227,6,19,0.3);
    }
    .brand-text h1 {
        color: var(--text);
        font-size: 1.55rem;
        margin: 0;
        font-weight: 800;
    }
    .brand-text .sub {
        color: var(--text-muted);
        font-size: 0.92rem;
        margin-top: 0.15rem;
        letter-spacing: 0.3px;
    }

    /* ===== Карточки ===== */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-top: 3px solid var(--red);
        border-radius: 12px;
        padding: 1.5rem 1.5rem 1.2rem 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        margin-bottom: 1.2rem;
    }
    .card h3 {
        font-size: 1.12rem;
        margin-top: 0;
        color: var(--text);
        border-left: 4px solid var(--red);
        padding-left: 0.65rem;
        margin-bottom: 1.1rem;
        font-weight: 700;
    }

    /* ===== Метрики ===== */
    .metric-box {
        background: var(--bg-soft);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
        height: 100%;
    }
    .metric-box .label {
        font-size: 0.78rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .metric-box .value {
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--text);
        margin-top: 0.35rem;
    }
    .metric-box .value.gold { color: var(--red); }

    /* ===== Бейджи вероятности ===== */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .badge-high   { background: #e3f5e8; color: #1b7a3d; }
    .badge-medium { background: #fff4e0; color: #a76a00; }
    .badge-low    { background: #fde8e8; color: #b42318; }

    /* Бейдж уверенности в весе */
    .conf {
        display:inline-block;
        padding:0.15rem 0.6rem;
        border-radius:14px;
        font-size:0.78rem;
        font-weight:600;
        margin-left:0.4rem;
    }
    .conf-high   { background:#e3f5e8; color:#1b7a3d; }
    .conf-medium { background:#fff4e0; color:#a76a00; }
    .conf-low    { background:#fde8e8; color:#b42318; }
    .conf-na     { background:#eceff3; color:#6b7280; }

    /* ===== Кнопка ===== */
    .stButton > button, .stFormSubmitButton > button {
        background: var(--red);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 0.65rem 1.4rem;
        font-weight: 700;
        font-size: 1rem;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background: var(--red-dark);
        color: #fff;
        box-shadow: 0 3px 12px rgba(227,6,19,0.3);
    }

    /* Прогресс-бар в фирменный красный */
    .stProgress > div > div > div > div {
        background-color: var(--red) !important;
    }

    .reason-item {
        padding: 0.45rem 0.75rem;
        background: var(--bg-soft);
        border-left: 3px solid var(--red);
        border-radius: 6px;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
        color: var(--text);
    }

    .weight-note {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-top: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== Брендовая шапка =====
st.markdown(
    """
    <div class="brand-bar">
        <div class="brand-logo">СКС</div>
        <div class="brand-text">
            <h1>СКС Ломбард — Уфа</h1>
            <div class="sub">Предварительная оценка ювелирных изделий по фотографиям</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Расчёт является предварительным и выполнен на основании фотографий и "
    "предоставленных данных. Вес, определённый по фотографии, носит "
    "оценочный характер. Окончательная оценка определяется специалистом "
    "после очного осмотра в подразделении компании."
)

left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="card"><h3>Данные изделия</h3>', unsafe_allow_html=True)
    with st.form("jewelry_form"):
        photos = st.file_uploader(
            "Фотографии изделия",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help="Загрузите 1–4 фотографии при хорошем освещении. "
                 "Для оценки веса полезно фото с линейкой или монетой рядом.",
        )

        c1, c2 = st.columns(2)
        with c1:
            item_type = st.selectbox(
                "Тип изделия",
                ["Кольцо", "Серьги", "Браслет", "Кулон", "Цепь", "Колье"],
            )
            sample = st.selectbox("Проба металла", ["375", "585", "750"])
        with c2:
            condition = st.selectbox("Состояние", ["Как новое", "Среднее", "Плохое"])
            weight = st.number_input(
                "Вес изделия, г (если известен)",
                min_value=0.0, step=0.1,
                help="Если вес неизвестен — оставьте 0, ИИ оценит его по фото.",
            )

        has_inserts = st.radio(
            "Наличие вставок", ["Нет", "Да"], horizontal=True
        ) == "Да"

        submitted = st.form_submit_button("Оценить изделие")
    st.markdown("</div>", unsafe_allow_html=True)


def _conf_badge(conf: str) -> str:
    mapping = {
        "высокая": ("conf-high", "высокая точность"),
        "средняя": ("conf-medium", "средняя точность"),
        "низкая":  ("conf-low", "низкая точность"),
    }
    cls, label = mapping.get(conf, ("conf-na", "нет данных"))
    return f'<span class="conf {cls}">{label}</span>'


with right:
    if not submitted:
        st.markdown(
            '<div class="card"><h3>Результат оценки</h3>'
            '<p style="color:#6b7280;">Заполните данные изделия и нажмите '
            '«Оценить изделие», чтобы получить предварительный расчёт.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        form_data = {
            "type": item_type,
            "sample": sample,
            "has_inserts": has_inserts,
            "condition": condition,
            # передаём вес из анкеты, если он указан (>0)
            "weight_g": weight if weight > 0 else None,
        }
        img_bytes = [p.read() for p in photos] if photos else []

        with st.spinner("Анализируем изделие..."):
            analysis = analyze_jewelry(img_bytes, form_data)

        # Определяем финальный вес для расчёта:
        # приоритет — анкета; иначе оценка ИИ по фото
        if weight > 0:
            final_weight = weight
            weight_is_estimated = False
        else:
            final_weight = analysis.get("estimated_weight_g") or 0
            weight_is_estimated = True

        price = calculate_price({
            "item_type": analysis["type"],
            "fineness": sample,
            "has_inserts": analysis["has_inserts"],
            "condition": analysis["condition"],
            "weight": final_weight,
        })
        prob = acceptance_probability({
            "condition": analysis["condition"],
            "has_inserts": analysis["has_inserts"],
            "weight": final_weight,
            # --- новые поля ---
            "has_defects": analysis.get("has_defects", False),
            "insert_damage": analysis.get("insert_damage", False),
            "defects_description": analysis.get("defects_description", ""),
            "defect_severity": analysis.get("defect_severity", "нет"),
            "repairable": analysis.get("repairable", True),
        })

        st.markdown('<div class="card"><h3>Результат оценки</h3>', unsafe_allow_html=True)

        # ===== Метрики =====
        ppg = f"{price['price_per_gram']:,}".replace(",", " ")
        total = (
            f"{price['total']:,} ₽".replace(",", " ")
            if price["total"] is not None else "— нет веса"
        )

        weight_display = (
            f"{final_weight:g} г" if final_weight else "—"
        )
        weight_label = "Вес (оценка по фото)" if weight_is_estimated else "Вес изделия"

        m1, m2, m3 = st.columns(3)
        m1.markdown(
            f'<div class="metric-box"><div class="label">{weight_label}</div>'
            f'<div class="value">{weight_display}</div></div>',
            unsafe_allow_html=True,
        )
        m2.markdown(
            f'<div class="metric-box"><div class="label">Цена за грамм</div>'
            f'<div class="value gold">{ppg} ₽</div></div>',
            unsafe_allow_html=True,
        )
        m3.markdown(
            f'<div class="metric-box"><div class="label">Предварительная сумма</div>'
            f'<div class="value gold">{total}</div></div>',
            unsafe_allow_html=True,
        )

        # ===== Информация об оценочном весе =====
        if weight_is_estimated and final_weight:
            conf = analysis.get("weight_confidence", "низкая")
            w_min = analysis.get("weight_min_g")
            w_max = analysis.get("weight_max_g")
            range_txt = ""
            if w_min and w_max:
                range_txt = f" Диапазон: {w_min:g}–{w_max:g} г."
            st.markdown(
                f'<div class="weight-note">⚖️ Вес определён по фотографии '
                f'{_conf_badge(conf)}.{range_txt} '
                f'{analysis.get("weight_reasoning", "")}</div>',
                unsafe_allow_html=True,
            )

        # ===== Вероятность =====
        score = prob["probability"]
        if score >= 80:
            badge_cls = "badge-high"
        elif score >= 50:
            badge_cls = "badge-medium"
        else:
            badge_cls = "badge-low"

        st.markdown(
            f'<p style="margin-top:1.2rem;">Вероятность принятия: '
            f'<span class="badge {badge_cls}">{prob["verdict"]} — {score}%</span></p>',
            unsafe_allow_html=True,
        )
        st.progress(score / 100)

        if prob["reasons"]:
            st.markdown("**Замечания:**", unsafe_allow_html=True)
            for r in prob["reasons"]:
                st.markdown(f'<div class="reason-item">{r}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ===== Детали ИИ =====
        with st.expander("Подробности анализа ИИ"):
            a1, a2 = st.columns(2)
            a1.write(f"**Тип изделия:** {analysis['type']}")
            a1.write(f"**Состояние:** {analysis['condition']}")
            a1.write(f"**Вставки:** {'Да' if analysis['has_inserts'] else 'Нет'}")
            a2.write(f"**Дефекты:** {'Да' if analysis['has_defects'] else 'Нет'}")
            a2.write(f"**Повреждение вставок:** {'Да' if analysis['insert_damage'] else 'Нет'}")
            a2.write(f"**Серьёзность дефектов:** {analysis.get('defect_severity', '—')}")
            a2.write(f"**Ремонтопригодно:** {'Да' if analysis.get('repairable', True) else 'Нет (только на лом)'}")
            st.write(f"**Описание дефектов:** {analysis['defects_description']}")
            st.write(f"**Визуальные заметки:** {analysis['visual_notes']}")

            st.markdown("---")
            st.markdown("**Оценка веса**")
            w1, w2 = st.columns(2)
            w1.write(f"**Источник:** {analysis.get('weight_source', '—')}")
            w1.write(f"**Оценочный вес:** "
                     f"{analysis.get('estimated_weight_g') or '—'} г")
            w2.write(f"**Диапазон:** "
                     f"{analysis.get('weight_min_g') or '—'}–"
                     f"{analysis.get('weight_max_g') or '—'} г")
            w2.write(f"**Уверенность:** {analysis.get('weight_confidence', '—')}")
            st.write(f"**Обоснование веса:** {analysis.get('weight_reasoning', '—')}")

        if photos:
            with st.expander("Загруженные фотографии"):
                cols = st.columns(min(len(photos), 4))
                for i, p in enumerate(photos):
                    cols[i % len(cols)].image(p)

        # ===== Предупреждения =====
        if weight_is_estimated:
            if final_weight:
                st.warning(
                    "Вес рассчитан автоматически по фотографии и является "
                    "приблизительным. Для точной суммы укажите фактический вес "
                    "или взвесьте изделие в подразделении."
                )
            else:
                st.error(
                    "Не удалось оценить вес по фотографии. Укажите вес вручную "
                    "для расчёта стоимости."
                )

        st.caption("Окончательная оценка — после очного осмотра специалистом.")