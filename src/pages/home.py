import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
import plotly.graph_objects as go


###############################
# Helpers
###############################

def load_home_css() -> None:
    """Inject CSS styles for the Home page from *static/home.css*.

    If the file cannot be found we fail silently so the rest of the page
    still renders.
    """
    css_path = Path("static/style.css")
    if css_path.exists():
        with css_path.open() as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS‑файл static/home.css не найден – страница показана без кастомных стилей.")


###############################
# Page
###############################

def show():
    """Главная страница AdsorpNET."""

    # 1. Load page‑specific styles -------------------------
    load_home_css()

    # 2. Header -------------------------------------------
    header_col1, header_col2 = st.columns([3, 1])

    with header_col1:
        st.markdown('<h1 class="logo-text">AdsorpNET</h1>', unsafe_allow_html=True)
        st.markdown('<p>AI‑сервис для разработки пористых материалов</p>', unsafe_allow_html=True)

    with header_col2:
        st.markdown(
            """
            <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px;">
                <a href="#" class="nav-link">🏠 Главная</a>
                <a href="#" class="nav-link">👤 Профиль</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. Tabs ---------------------------------------------
    tab1, tab2, tab3 = st.tabs(["🔍 Обзор", "🧪 AI синтез MOFs", "📊 Аналитика"])

    # ------------------------------------------------------------------
    # TAB 1 – Обзор / Hero‑секция
    # ------------------------------------------------------------------
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        hero_col1, hero_col2 = st.columns([3, 2])

        # --- Hero: описание & CTA ------------------------------------
        with hero_col1:
            st.markdown('<h2 class="accent-header">Добро пожаловать в AdsorpNET!</h2>', unsafe_allow_html=True)
            st.markdown(
                """
                Инновационный AI‑сервис для разработки пористых материалов с применением 
                передовых методов машинного обучения для предсказания оптимальных параметров синтеза 
                металлорганических каркасных структур (MOFs).
                """
            )
            st.button("Начать работу с AI")

        # --- Hero: изображение ---------------------------------------
        with hero_col2:
            img_path = Path("images/MOF_Synthesis_Prediction.png")
            if img_path.exists():
                st.image(str(img_path), width=300)
            else:
                # Fallback визуализация – простая 3‑D scatter
                fig = go.Figure(
                    data=[
                        go.Scatter3d(
                            x=[0, 1, 2, 0, 1, 2, 0, 1, 2],
                            y=[0, 0, 0, 1, 1, 1, 2, 2, 2],
                            z=[0, 1, 0, 1, 0, 1, 0, 1, 0],
                            mode="markers",
                            marker=dict(
                                size=12,
                                color=[
                                    "blue",
                                    "red",
                                    "green",
                                    "blue",
                                    "red",
                                    "green",
                                    "blue",
                                    "red",
                                    "green",
                                ],
                                opacity=0.8,
                            ),
                        )
                    ]
                )
                fig.update_layout(
                    margin=dict(l=0, r=0, b=0, t=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    scene=dict(
                        xaxis=dict(showticklabels=False, title=""),
                        yaxis=dict(showticklabels=False, title=""),
                        zaxis=dict(showticklabels=False, title=""),
                    ),
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)
        

         # Key metrics in cards
        st.markdown('<h3 class="accent-header">Ключевые характеристики MOF</h3>', unsafe_allow_html=True)
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">500 °C</div>
                <div class="metric-label">Термическая стабильность</div>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">800+ м²/г</div>
                <div class="metric-label">Удельная поверхность</div>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">0.2 г/см³</div>
                <div class="metric-label">Насыпная плотность</div>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">3-100 Å</div>
                <div class="metric-label">Размеры пор</div>
            </div>
            """, unsafe_allow_html=True)
        
        # About MOF section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="accent-header">О Metal-Organic Frameworks (MOF)</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        Metal-Organic Frameworks (MOF) — класс кристаллических материалов, признанных одной из
        «десяти лучших новых технологий в химии» по версии IUPAC. Сочетание металлических кластеров
        и органических лигандов при синтезе MOF создаёт материалы с уникальными свойствами.
        """)
        
        # Visualize MOF structure and applications
        mof_col1, mof_col2 = st.columns(2)
        
        with mof_col1:
            st.markdown('<h4>Структура MOF</h4>', unsafe_allow_html=True)
            
            # Example data for radar chart
            categories = ['Пористость', 'Термостабильность', 'Селективность', 'Каталитическая активность', 'Стоимость']
            values = [9, 8, 7, 9, 6]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='MOF-характеристики',
                line_color='#4e54c8',
                fillcolor='rgba(78, 84, 200, 0.2)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=False,
                margin=dict(l=10, r=10, b=10, t=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with mof_col2:
            st.markdown('<h4>Области применения</h4>', unsafe_allow_html=True)
            st.markdown("""
            <div class="feature-box">
                <strong>Хранение газов</strong> — водород, метан, углекислый газ
            </div>
            <div class="feature-box">
                <strong>Разделение газов</strong> — очистка природного газа, захват CO₂
            </div>
            <div class="feature-box">
                <strong>Катализ</strong> — химические реакции, фотокатализ
            </div>
            <div class="feature-box">
                <strong>Сенсоры</strong> — обнаружение газов, ионов, биомолекул
            </div>
            <div class="feature-box">
                <strong>Медицина</strong> — доставка лекарств, визуализация, терапия
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Features section
        st.markdown('<h3 class="accent-header">Возможности системы</h3>', unsafe_allow_html=True)
        
        features_col1, features_col2 = st.columns(2)
        
        with features_col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h4>🔬 Предсказание параметров синтеза</h4>', unsafe_allow_html=True)
            st.markdown("""
            Наша AI-система позволяет предсказать оптимальные параметры синтеза MOF на основе желаемых 
            характеристик конечного материала:
            - Подбор металлических кластеров
            - Выбор органических лигандов
            - Определение оптимального растворителя
            - Расчет температуры и времени синтеза
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h4>🧪 Оптимизация условий синтеза</h4>', unsafe_allow_html=True)
            st.markdown("""
            Система анализирует множество факторов для оптимизации условий синтеза:
            - Анализ существующих экспериментальных данных
            - Оценка влияния различных параметров
            - Расчет оптимальных соотношений компонентов
            - Моделирование процесса кристаллизации
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with features_col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h4>📊 Анализ структурных характеристик</h4>', unsafe_allow_html=True)
            st.markdown("""
            Проводим комплексный анализ существующих MOF материалов:
            - Расчет удельной поверхности
            - Определение объема и распределения пор
            - Оценка термической стабильности
            - Прогнозирование сорбционных свойств
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h4>📈 Прогнозирование свойств</h4>', unsafe_allow_html=True)
            st.markdown("""
            Используя методы машинного обучения, система предсказывает:
            - Сорбционные характеристики
            - Селективность к различным газам
            - Каталитическую активность
            - Химическую и механическую стабильность
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Synthesis Tab (placeholder)
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="accent-header">AI синтез Metal-Organic Frameworks</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        Задайте желаемые параметры для вашего MOF материала и наша система предложит оптимальные условия синтеза.
        """)
        
        # Input form for MOF parameters
        form_col1, form_col2 = st.columns(2)
        
        with form_col1:
            st.markdown("### Целевые характеристики")
            surface_area = st.slider("Удельная поверхность (м²/г)", 500, 2000, 1000)
            pore_size = st.slider("Размер пор (Å)", 5, 50, 20)
            thermal_stability = st.slider("Термическая стабильность (°C)", 200, 600, 400)
            
            st.markdown("### Предпочтения по компонентам")
            metal_options = ["Zn", "Cu", "Al", "Fe", "Zr", "Ti", "Cr", "Ni", "Co", "Mg"]
            metals = st.multiselect("Предпочтительные металлы", metal_options)
            
            ligand_types = ["Дикарбоксилатные", "Трикарбоксилатные", "Азотсодержащие", "Сульфосодержащие"]
            ligands = st.multiselect("Типы лигандов", ligand_types)
        
        with form_col2:
            st.markdown("### Условия синтеза")
            method = st.selectbox("Метод синтеза", ["Сольвотермальный", "Механохимический", "Микроволновый", "Ультразвуковой"])
            
            st.markdown("### Приложение")
            applications = st.multiselect("Целевое применение", 
                ["Хранение H₂", "Захват CO₂", "Разделение газов", "Катализ", "Доставка лекарств", "Сенсоры"])
            
            st.markdown("### Ограничения")
            constraints = st.multiselect("Ограничения", 
                ["Экологическая безопасность", "Низкая стоимость", "Масштабируемость", "Водостойкость"])
        
        # Submit button
        if st.button("Рассчитать параметры синтеза"):
            st.markdown('<div class="card" style="margin-top: 20px;">', unsafe_allow_html=True)
            st.markdown('<h3 class="accent-header">Рекомендуемые параметры синтеза</h3>', unsafe_allow_html=True)
            
            # Display recommendations (placeholder)
            rec_col1, rec_col2 = st.columns(2)
            
            with rec_col1:
                st.markdown("### Компоненты")
                st.markdown("**Рекомендуемые металлы:** Zn²⁺, Cu²⁺")
                st.markdown("**Рекомендуемый лиганд:** 1,4-бензолдикарбоновая кислота (BDC)")
                st.markdown("**Оптимальный растворитель:** N,N-диметилформамид (DMF)")
                
                st.markdown("### Ожидаемые свойства")
                st.markdown(f"**Удельная поверхность:** {surface_area + 200} м²/г")
                st.markdown(f"**Размер пор:** {pore_size + 2} Å")
                st.markdown(f"**Термическая стабильность:** {thermal_stability + 30} °C")
                
            with rec_col2:
                st.markdown("### Параметры синтеза")
                st.markdown("**Температура:** 120 °C")
                st.markdown("**Время синтеза:** 24 ч")
                st.markdown("**pH среды:** 6.5-7.0")
                st.markdown("**Соотношение металл:лиганд:** 1:1.5")
                
                # Visualization of confidence
                confidence_data = {
                    "Параметр": ["Металл", "Лиганд", "Растворитель", "Температура", "Время"],
                    "Уверенность (%)": [92, 88, 95, 85, 80]
                }
                confidence_df = pd.DataFrame(confidence_data)
                
                fig = go.Figure(go.Bar(
                    x=confidence_df["Уверенность (%)"],
                    y=confidence_df["Параметр"],
                    orientation='h',
                    marker_color='#4e54c8',
                    text=confidence_df["Уверенность (%)"].astype(str) + '%',
                    textposition='auto'
                ))
                
                fig.update_layout(
                    title="Уверенность AI в рекомендациях",
                    xaxis_title="Уверенность (%)",
                    yaxis_title="",
                    margin=dict(l=0, r=10, t=30, b=0),
                    height=250,
                    xaxis=dict(range=[0, 100])
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### Протокол синтеза")
            st.markdown("""
            1. Подготовить раствор Zn(NO₃)₂·6H₂O (0.297 г, 1 ммоль) в 15 мл DMF.
            2. Добавить 1,4-бензолдикарбоновую кислоту (0.249 г, 1.5 ммоль) и перемешать до полного растворения.
            3. Перенести раствор в тефлоновый автоклав объемом 50 мл.
            4. Нагреть автоклав до 120 °C и выдержать в течение 24 часов.
            5. Охладить до комнатной температуры в течение 12 часов.
            6. Отфильтровать полученные кристаллы, промыть DMF (3 × 10 мл) и метанолом (3 × 10 мл).
            7. Сушить при 80 °C в вакууме в течение 12 часов.
            """)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Analytics Tab (placeholder)
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="accent-header">Аналитика MOF материалов</h2>', unsafe_allow_html=True)
        
        # Example dataset
        mof_data = {
            "MOF": ["MOF-5", "HKUST-1", "UiO-66", "ZIF-8", "MIL-101", "NU-1000", "MOF-74"],
            "Металл": ["Zn", "Cu", "Zr", "Zn", "Cr", "Zr", "Zn"],
            "Удельная поверхность (м²/г)": [3800, 1900, 1200, 1700, 4100, 2200, 1300],
            "Объем пор (см³/г)": [1.55, 0.75, 0.50, 0.65, 2.15, 1.40, 0.55],
            "Температурная стабильность (°C)": [400, 350, 450, 300, 300, 500, 350]
        }
        df = pd.DataFrame(mof_data)
        
        # Data exploration section
        st.markdown("### Сравнительный анализ MOF материалов")
        
        # Visualization selector
        viz_type = st.selectbox("Выберите тип визуализации", 
                               ["Удельная поверхность", "Объем пор", "Температурная стабильность", "Корреляционный анализ"])
        
        if viz_type == "Удельная поверхность":
            fig = go.Figure(go.Bar(
                x=df["MOF"],
                y=df["Удельная поверхность (м²/г)"],
                marker_color='#4e54c8',
                text=df["Удельная поверхность (м²/г)"],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Удельная поверхность различных MOF",
                xaxis_title="MOF",
                yaxis_title="Удельная поверхность (м²/г)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Объем пор":
            fig = go.Figure(go.Bar(
                x=df["MOF"],
                y=df["Объем пор (см³/г)"],
                marker_color='#8f94fb',
                text=df["Объем пор (см³/г)"],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Объем пор различных MOF",
                xaxis_title="MOF",
                yaxis_title="Объем пор (см³/г)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Температурная стабильность":
            fig = go.Figure(go.Bar(
                x=df["MOF"],
                y=df["Температурная стабильность (°C)"],
                marker_color='#5a67d8',
                text=df["Температурная стабильность (°C)"],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Температурная стабильность различных MOF",
                xaxis_title="MOF",
                yaxis_title="Температурная стабильность (°C)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:  # Correlation analysis
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df["Удельная поверхность (м²/г)"],
                y=df["Объем пор (см³/г)"],
                mode='markers+text',
                text=df["MOF"],
                textposition="top center",
                marker=dict(
                    size=12,
                    color=df["Температурная стабильность (°C)"],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Температурная<br>стабильность (°C)")
                )
            ))
            
            fig.update_layout(
                title="Корреляция между удельной поверхностью и объемом пор",
                xaxis_title="Удельная поверхность (м²/г)",
                yaxis_title="Объем пор (см³/г)",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table with search
        st.markdown("### База данных MOF материалов")
        search_term = st.text_input("Поиск по MOF или металлу")
        
        if search_term:
            filtered_df = df[df.apply(lambda row: search_term.lower() in str(row["MOF"]).lower() or 
                                       search_term.lower() in str(row["Металл"]).lower(), axis=1)]
        else:
            filtered_df = df
        
        st.dataframe(filtered_df, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar sections removed - statistics, recent projects, and help are no longer displayed
