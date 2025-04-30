"""
Страница предсказания методики синтеза MOF.
Исправленная версия с нативными компонентами Streamlit.
"""

import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Union, Tuple, Optional
import os
import time

from src.utils.ui import load_theme_css
from src.services.predictor_service import PredictorService

# --- Константы ---
PRIMARY_COLOR = "#4361ee"
SECONDARY_COLOR = "#4cc9f0"
SUCCESS_COLOR = "#06d6a0"
WARNING_COLOR = "#ffd166"
DANGER_COLOR = "#ef476f"

# --- Утилиты ---

def get_img_as_base64(file_path: str) -> str:
    """
    Преобразует изображение в base64 для встраивания в HTML.
    Возвращает прозрачный пиксель, если файл не найден.
    """
    if not os.path.exists(file_path):
        # Возвращаем прозрачный пиксель в base64
        return "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    except Exception as e:
        # Логируем ошибку, но не показываем пользователю
        print(f"Ошибка чтения файла {file_path}: {e}")
        return "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

@st.cache_data(show_spinner=False)
def load_icon_map() -> Dict[str, str]:
    """Предзагрузка и кэширование иконок"""
    icon_dir = Path("images")
    icons = {
        "Металл": "Metal.png",
        "Лиганд": "Ligand.png",
        "Растворитель": "Solvent.png",
        "m (соли), г": "SaltMass.png",
        "m(кис-ты), г": "AcidMass.png",
        "Vсин. (р-ля), мл": "Vsyn.png",
        "Т.син., °С": "Tsyn.png",
        "Т суш., °С": "Tdry.png",
        "Tрег, ᵒС": "Treg.png",
    }
    
    icon_map = {}
    for name, file in icons.items():
        try:
            path = icon_dir / file
            with path.open("rb") as f:
                icon_map[name] = base64.b64encode(f.read()).decode()
        except (FileNotFoundError, IOError) as e:
            # Тихо продолжаем без иконки
            icon_map[name] = ""
    
    return icon_map

# --- Минимальные стили CSS для улучшения внешнего вида ---

def inject_minimal_css() -> None:
    """Внедряет минимум необходимых стилей для улучшения внешнего вида"""
    css = """
    <style>
    /* Основные стили, не использующие сложный HTML */
    
    
    /* Контейнер списка вкладок */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;                       /* убираем белый фон */
        border: none;                                  /* без рамки */
        gap: 0;                                        /* плотно друг к другу */
        border-bottom: 1px solid rgba(255,255,255,.15);/* тонкий разделитель */
    }

    /* Каждая вкладка */
    .stTabs [data-baseweb="tab"] {
        background: transparent;                       /* прозрачный фон */
        color: rgba(255,255,255,.6);                   /* бледный текст */
        padding: 8px 20px;
        font-weight: 500;
        transition: color .2s;
        border: none;                                  /* убираем внутренние рамки */
    }

    /* Ховер по неактивной вкладке */
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        color: #ffffff;                                /* подсвечиваем текст */
    }

    /* Активная вкладка */
    .stTabs [aria-selected="true"] {
        color: #ffffff;
        background: rgba(67,97,238,.15);               /* лёгкая заливка */
        border-bottom: 3px solid #4361ee;              /* подчёркивание фирменным цветом */
        font-weight: 600;
    }

    /* Сброс густых внутренних границ, которые рисует baseweb */
    .stTabs [data-baseweb="tab"]::before,
    .stTabs [data-baseweb="tab"]::after {
        display: none;
    }
    
    /* ── отключаем синее подчёркивание активной вкладки ────────────── */
    .stTabs [aria-selected="true"] {
        border-bottom: none !important;   /* было 3px solid #4361ee */
    }

    
    
    
    /* Основные стили для текста */
    h1, h2, h3 {
        margin-bottom: 0.5rem; /* Уменьшенный отступ после заголовков */
    }
    
    h1 {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    h2 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    h3 {
        font-size: 1.25rem;
        font-weight: 600;
        margin-top: 1.25rem;
        color: #2c3e50;
        border-bottom: none; /* Убран разделитель */
        padding-bottom: 0px; /* Убран отступ под заголовком */
        margin-bottom: 10px; /* Уменьшен отступ после заголовка */
    }
    
    
    /* Улучшение стилей для полей ввода - убираем белые разделители и контур */
    div[data-testid="stNumberInput"] {
    margin-bottom: 10px;
    margin-top: 5px;
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    padding: 8px !important;
    position: relative !important;
}
    
    /* Убираем белый контур вокруг полей ввода */
    input[type="number"] {
    border: none !important;
    box-shadow: none !important;
    background-color: transparent !important;
    color: white !important;
}
    
    /* Отображение меток в одну строку и без описания */
    div[data-testid="stNumberInput"] label {
        border-left: 3px solid #4361ee;
        padding-left: 8px;
        font-weight: 500;
        white-space: nowrap;
        overflow: visible;
        width: auto;
        display: inline-block;
        max-width: 85%; /* Ограничиваем ширину метки для освобождения места для иконки */
    }
    
    /* Стиль для контейнера метки */
    div[data-testid="stNumberInput"] > div:first-child {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-direction: row !important;
        width: 100% !important;
    }
    
    /* Стиль для иконки помощи */
    div[data-testid="stNumberInput"] [data-testid="stTooltipIcon"] {
        position: absolute !important;
        right: 10px !important;
        top: 10px !important;
        margin-left: auto !important;
    }
    
    /* Дополнительная фиксация иконок */
    div[data-baseweb="tooltip"] {
        display: inline-block !important;
        position: relative !important;
        left: auto !important;
        right: 0 !important;
    }
    
    /* Скрываем текст описания после параметров */
    div[data-testid="stNumberInput"] + div[data-testid="stText"] {
        display: none !important;
    }
    
    /* Улучшаем вид info-блоков */
    div.stAlert {
        border-radius: 8px;
        border-left-width: 3px;
        margin: 15px 0 15px 0;
    }
    
    div.stAlert[data-baseweb="notification"] {
        background-color: #e7f5ff;
    }
    
    /* Кнопка рассчета */
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #4361ee;
        font-weight: 600;
        border-radius: 8px;
    }
    
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #3a56d4;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Заголовок экспандера */
    button[data-testid="stExpander"] {
        background-color: #f8f9fa;
        border-radius: 6px;
        border: none;
        padding: 10px;
    }
    
    /* Содержимое экспандера */
    div[data-testid="stExpander-content"] {
        border: 1px solid #f1f3f5;
        border-radius: 0 0 8px 8px;
        padding: 10px 15px;
    }
    
    /* контрастные чипы для тёмной темы */
    .alt-chip {
        display:inline-block;
        padding:4px 12px;
        margin:4px 6px 4px 0;
        border-radius:20px;
        background:rgba(255,255,255,.08);  /* лёгкая подсветка */
        color:#ffffff;                     /* белый текст */
        font-size:14px;
        line-height:20px;
        white-space:nowrap;
    }


    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Компоненты UI, использующие нативный Streamlit ---

def render_step_indicator(current_step: int) -> None:
    """
    Отображает индикатор прогресса с использованием нативных компонентов Streamlit.
    
    Args:
        current_step: Номер текущего шага (0-indexed)
    """
    steps = ["Ввод данных", "Анализ ML", "Результаты"]
    col1, col2, col3 = st.columns(3)
    
    # Определяем цвета для шагов
    step_colors = ["#dddddd"] * 3  # Серый цвет по умолчанию
    text_colors = ["#666666"] * 3  # Серый текст по умолчанию
    
    # Цвета для выполненных и текущего шага
    for i in range(current_step):
        step_colors[i] = SUCCESS_COLOR  # Выполненные шаги зеленые
        text_colors[i] = SUCCESS_COLOR
    
    if current_step < 3:
        step_colors[current_step] = PRIMARY_COLOR  # Текущий шаг синий
        text_colors[current_step] = PRIMARY_COLOR
    
    # Создаем колонки со статусами
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="background-color: {step_colors[0]}; color: white; 
                 width: 30px; height: 30px; border-radius: 50%; display: inline-flex; 
                 align-items: center; justify-content: center; font-weight: bold; margin-bottom: 5px;">
                1
            </div>
            <div style="color: {text_colors[0]}; font-weight: {'bold' if current_step == 0 else 'normal'};">
                {steps[0]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="background-color: {step_colors[1]}; color: white; 
                 width: 30px; height: 30px; border-radius: 50%; display: inline-flex; 
                 align-items: center; justify-content: center; font-weight: bold; margin-bottom: 5px;">
                2
            </div>
            <div style="color: {text_colors[1]}; font-weight: {'bold' if current_step == 1 else 'normal'};">
                {steps[1]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="background-color: {step_colors[2]}; color: white; 
                 width: 30px; height: 30px; border-radius: 50%; display: inline-flex; 
                 align-items: center; justify-content: center; font-weight: bold; margin-bottom: 5px;">
                3
            </div>
            <div style="color: {text_colors[2]}; font-weight: {'bold' if current_step == 2 else 'normal'};">
                {steps[2]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    

def render_input_form() -> Tuple[bool, Dict[str, float], Dict[str, float]]:
    """
    Отрисовывает форму ввода параметров с нативными компонентами Streamlit.
    
    Returns:
        Tuple[bool, Dict[str, float], Dict[str, float]]: 
            - Флаг отправки формы
            - Введенные параметры
            - Расчетные параметры
    """
    # Используем стандартные компоненты Streamlit для контейнеров
    with st.container():
        st.subheader("Целевые характеристики материала")
        st.write("Введите желаемые параметры будущего MOF, и система предскажет оптимальную методику синтеза.")
        
        # Группа 1: Основные параметры поверхности
        st.markdown("### Параметры поверхности")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            SBAT_m2_gr = st.number_input(
                "SБЭТ, м²/г · Диапазон: 500-3000 м²/г",
                min_value=100.0, value=1200.0, step=10.0,
                help="Удельная площадь поверхности. Определяет доступную поверхность материала для адсорбции.",
                key="SBAT_m2_gr"
            )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            a0_mmoll_gr = st.number_input(
                "а₀, ммоль/г · Диапазон: 5-20 ммоль/г",
                min_value=0.1, value=10.5, step=0.1,
                help="Предельная адсорбция. Максимальное количество адсорбата, которое может поглотить материал.",
                key="a0_mmoll_gr"
            )
        
        # Группа 2: Энергетические параметры
        st.markdown("### Энергетические параметры")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            E_kDg_moll = st.number_input(
                "E (азот), кДж/моль · Диапазон: 5-10 кДж/моль",
                min_value=0.1, value=6.5, step=0.1,
                help="Энергия адсорбции азота. Характеризует силу взаимодействия адсорбента с азотом.",
                key="E_kDg_moll"
            )
        
        # Расчет зависимых параметров
        W0_cm3_g = 0.034692 * a0_mmoll_gr if a0_mmoll_gr else 0
        # Избегаем деления на слишком маленькие числа
        E0_KDG_moll = E_kDg_moll / 0.33 if E_kDg_moll and E_kDg_moll > 0 else 0.1
        x0_nm = 12 / E0_KDG_moll if E0_KDG_moll > 0 else 0  # Проверка деления на ноль
        approx_Ws_cm3_gr = W0_cm3_g * 1.2  # Приблизительная оценка
        
        # Показываем расчет объема пор через st.info()
        st.info(f"Расчетный объем микропор (W₀): {W0_cm3_g:.4f} см³/г")
        st.info(f"Расчетный общий объем пор: {approx_Ws_cm3_gr:.4f} см³/г")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            Ws_cm3_gr = st.number_input(
                "Ws, см³/г · Должен быть > W₀",
                min_value=0.01, value=float(f"{approx_Ws_cm3_gr:.4f}") if approx_Ws_cm3_gr > 0 else 0.1, step=0.01,
                help="Общий объем пор материала. Обычно немного больше объема микропор (W₀).",
                key="Ws_cm3_gr",
                format="%.4f"
            )
        
        # Группа 3: Параметры мезопор
        st.markdown("### Параметры мезопор")
        
        # Расчет объема мезопор
        Wme_cm3_gr = Ws_cm3_gr - W0_cm3_g if Ws_cm3_gr and W0_cm3_g and Ws_cm3_gr > W0_cm3_g else 0.0
        st.info(f"Расчетный объем мезопор (Wme): {Wme_cm3_gr:.4f} см³/г")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            Sme_m2_gr = st.number_input(
                "Sme, м²/г · 10-30% от общей площади",
                min_value=0.0, value=200.0, step=10.0,
                help="Площадь поверхности мезопор (размер пор 2-50 нм).",
                key="Sme_m2_gr"
            )

        # Расширенная информация о параметрах
        with st.expander("Все расчетные параметры и формулы", expanded=False):
            st.write("**Основные параметры и их взаимосвязь:**")
            st.write("- **W₀** (объем микропор): `0.034692 × а₀`")
            st.write("- **E₀** (характеристическая энергия адсорбции): `E / 0.33`")
            st.write("- **x₀** (полуширина микропор): `12 / E₀`")
            st.write("- **Wme** (объем мезопор): `Ws - W₀`")
            
            # Таблица расчетных параметров для наглядности
            data = {
                "Параметр": ["W₀ (объем микропор)", "E₀ (хар. энергия)", "x₀ (полуширина)", "Wme (объем мезопор)"],
                "Формула": ["0.034692 × а₀", "E / 0.33", "12 / E₀", "Ws - W₀"],
                "Значение": [f"{W0_cm3_g:.4f}", f"{E0_KDG_moll:.4f}", f"{x0_nm:.4f}", f"{Wme_cm3_gr:.4f}"],
                "Единицы": ["см³/г", "кДж/моль", "нм", "см³/г"]
            }
            st.table(pd.DataFrame(data))
        
        # Проверка валидности ввода
        valid_inputs = (
            SBAT_m2_gr >= 100.0 and
            a0_mmoll_gr > 0 and
            E_kDg_moll > 0 and
            Ws_cm3_gr > 0 and
            Sme_m2_gr >= 0 and
            Ws_cm3_gr > W0_cm3_g  # Общий объем должен быть больше объема микропор
        )
        
        # Сообщение об ошибке, если что-то не так
        if not valid_inputs:
            st.warning("""
            Проверьте введенные параметры:
            - SБЭТ должна быть не менее 100 м²/г
            - Значения а₀, E и Ws должны быть положительными
            - Общий объем пор (Ws) должен быть больше объема микропор (W₀)
            """)
        
        # Разделитель перед кнопкой
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Кнопка отправки
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.button(
                "🔬 Рассчитать методику синтеза",
                type="primary",
                use_container_width=True,
                disabled=not valid_inputs,
                help="Запустить расчет оптимальных параметров синтеза MOF на основе введенных целевых характеристик."
            )
        
        # Возвращаем флаг нажатия кнопки и введенные значения
        input_values = {
            'SBAT_m2_gr': SBAT_m2_gr,
            'a0_mmoll_gr': a0_mmoll_gr,
            'E_kDg_moll': E_kDg_moll,
            'Ws_cm3_gr': Ws_cm3_gr,
            'Sme_m2_gr': Sme_m2_gr
        }
        
        derived_params = {
            'W0_cm3_g': W0_cm3_g,
            'E0_KDG_moll': E0_KDG_moll,
            'x0_nm': x0_nm,
            'Wme_cm3_gr': Wme_cm3_gr
        }
        
        return submitted, input_values, derived_params

def display_predicted_parameters(parameters: List[Dict[str, Any]]) -> None:
    """
    Отображает предсказанные параметры с использованием карточек.
    
    Args:
        parameters: Список словарей с параметрами и их метаданными
    """
    st.subheader("Оптимальные параметры синтеза")
    st.write(
        "Модель подобрала оптимальные условия синтеза MOF. "
        "Уверенность отображается для категориальных предсказаний."
    )

    # Группировка параметров по категориям для вкладок
    categories = {
        "Компоненты":  ["Металл", "Лиганд", "Растворитель"],
        "Пропорции":   ["m (соли), г", "m(кис-ты), г", "Vсин. (р-ля), мл"],
        "Температуры": ["Т.син., °С", "Т суш., °С", "Tрег, ᵒС"],
    }
    
    # Добавляем CSS для карточек параметров
    st.markdown("""
    <style>
    .param-card {
        background: rgba(30, 40, 60, 0.6);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4), 
                    0 2px 4px rgba(0, 0, 0, 0.3), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 0 3px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .param-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5), 
                    0 4px 8px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.15),
                    inset 0 0 5px rgba(255, 255, 255, 0.15);
    }
    
    .param-content {
        display: flex;
        align-items: center;
    }
    
    .param-icon {
        flex: 0 0 80px;
        margin-right: 20px;
    }
    
    .param-icon img {
        width: 80px;
        height: 80px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
    }
    
    .param-info {
        flex: 1;
    }
    
    .param-name {
        font-weight: 600;
        color: rgba(255, 255, 255, 0.85);
        margin-bottom: 5px;
    }
    
    .param-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #4cc9f0;
        margin-bottom: 10px;
    }
    
    .emoji-icon {
        font-size: 3rem;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 80px;
        height: 80px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Создаем вкладки
    tab_titles = list(categories.keys())
    tabs = st.tabs(tab_titles)
    
    # Отображаем параметры во вкладках
    for tab_idx, (tab_title, tab) in enumerate(zip(tab_titles, tabs)):
        with tab:
            for param_name in categories[tab_title]:
                # Находим параметр в списке
                param = next((p for p in parameters if p["name"] == param_name), None)
                if not param:
                    continue
                
                # Создаем колонки для карточки
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    # Отображаем иконку
                    if param.get("image_base64"):
                        st.image(param["image_base64"], width=80)
                    else:
                        emoji = {"Металл": "⚗️", "Лиганд": "🔬", "Растворитель": "💧"}.get(param["name"], "🧪")
                        st.markdown(f'<div class="emoji-icon">{emoji}</div>', unsafe_allow_html=True)
                
                with col2:
                    # Отображаем информацию о параметре
                    st.markdown(f'<div class="param-name">{param["name"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="param-value">{param["value"]}</div>', unsafe_allow_html=True)
                    
                    # Добавляем индикатор уверенности, если он есть
                    if param.get("prob") is not None:
                        confidence_value = param["prob"] * 100
                        st.markdown(f"**Уверенность модели:** {confidence_value:.1f}%")
                        st.progress(float(param["prob"]))
                
                
                # Добавляем разделитель между карточками
                st.markdown("<hr style='margin: 20px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    

# Функция для генерации HTML для иконки
def generate_icon_html(param: Dict[str, Any]) -> str:
    """Создает HTML-код для отображения иконки параметра"""
    if param.get("image_base64"):
        return f"""
        <img src="{param['image_base64']}" 
             style="width: 80px; height: 80px; 
                    border: 2px solid white; 
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(255,255,255,0.3);">
        """
    else:
        emoji = {"Металл": "⚗️", "Лиганд": "🔬", "Растворитель": "💧"}.get(param["name"], "🧪")
        return f"<div style='font-size:3rem;text-align:center'>{emoji}</div>"

def format_prediction_results_for_display(prediction_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Форматирует результаты предсказаний для отображения.
    
    Args:
        prediction_results: Результаты предсказаний
    
    Returns:
        List[Dict[str, Any]]: Форматированные результаты для отображения
    """
    # Загружаем иконки
    icon_folder = "images"
    icon_map = load_icon_map()
    
    # Формируем список параметров с метаданными
    parameters = [
        {
            "name": "Металл",
            "image": os.path.join(icon_folder, "Metal.png"),
            "image_base64": f"data:image/png;base64,{icon_map.get('Металл', '')}",
            "value": prediction_results.get('metal', {}).get('metal_type', 'N/A'),
            "prob": prediction_results.get('metal', {}).get('confidence'),
            "alternatives": prediction_results.get('metal', {}).get('alternatives', [
                {"value": "Fe", "probability": 82.5},
                {"value": "Al", "probability": 65.3}
            ])
        },
        {
            "name": "Лиганд",
            "image": os.path.join(icon_folder, "Ligand.png"),
            "image_base64": f"data:image/png;base64,{icon_map.get('Лиганд', '')}",
            "value": prediction_results.get('ligand', {}).get('ligand_type', 'N/A'),
            "prob": prediction_results.get('ligand', {}).get('confidence'),
            "alternatives": prediction_results.get('ligand', {}).get('alternatives', [
                {"value": "BTC", "probability": 78.2},
                {"value": "NH2-BDC", "probability": 56.8}
            ])
        },
        {
            "name": "Растворитель",
            "image": os.path.join(icon_folder, "Solvent.png"),
            "image_base64": f"data:image/png;base64,{icon_map.get('Растворитель', '')}",
            "value": prediction_results.get('solvent', {}).get('solvent_type', 'N/A'),
            "prob": prediction_results.get('solvent', {}).get('confidence'),
            "alternatives": prediction_results.get('solvent', {}).get('alternatives', [
                {"value": "ДМФА/Этанол/Вода", "probability": 75.9},
                {"value": "ДМФА", "probability": 68.4}
            ])
        },
        {
            "name": "m (соли), г",
            "image": os.path.join(icon_folder, "SaltMass.png"),
            "image_base64": f"data:image/png;base64,{icon_map.get('m (соли), г', '')}",
            "value": f"{prediction_results.get('salt_mass', 0):.3f}",
            "prob": None
        },
        {
            "name": "m(кис-ты), г",
            "image": os.path.join(icon_folder, "AcidMass.png"),
            "image_base64": f"data:image/png;base64,{icon_map.get('m(кис-ты), г', '')}",
            "value": f"{prediction_results.get('acid_mass', 0):.3f}",
            "prob": None
        },
        {
            "name": "Vсин. (р-ля), мл",
            "image": os.path.join(icon_folder, "Vsyn.png"),
            "image_base64": f"data:image/png;base64,{icon_map.get('Vсин. (р-ля), мл', '')}",
            "value": f"{prediction_results.get('synthesis_volume', 0):.1f}",
            "prob": None
        },
        {
            "name": "Т.син., °С",
            "image": os.path.join(icon_folder, "Tsyn.png"),
            "image_base64": f"data:image/png;base64,{icon_map.get('Т.син., °С', '')}",
            "value": prediction_results.get('tsyn', {}).get('temperature', 'N/A'),
            "prob": prediction_results.get('tsyn', {}).get('confidence')
        },
        {
            "name": "Т суш., °С",
            "image": os.path.join(icon_folder, "Tdry.png"),
            "image_base64": f"data:image/png;base64,{icon_map.get('Т суш., °С', '')}",
            "value": prediction_results.get('tdry', {}).get('temperature', 'N/A'),
            "prob": prediction_results.get('tdry', {}).get('confidence')
        },
        {
            "name": "Tрег, ᵒС",
            "image": os.path.join(icon_folder, "Treg.png"),
            "image_base64": f"data:image/png;base64,{icon_map.get('Tрег, ᵒС', '')}",
            "value": prediction_results.get('treg', {}).get('temperature', 'N/A'),
            "prob": prediction_results.get('treg', {}).get('confidence')
        },
    ]
    
    return parameters

def prepare_download_df(
    input_params: Dict[str, float],
    prediction_results: Dict[str, Any],
    derived_params: Dict[str, float]
) -> pd.DataFrame:
    """
    Подготавливает DataFrame для скачивания результатов.
    
    Args:
        input_params: Входные параметры
        prediction_results: Результаты предсказаний
        derived_params: Расчетные параметры
    
    Returns:
        pd.DataFrame: DataFrame для скачивания
    """
    # Набор параметров для отчета
    data = {
        'Параметр': [
            # Входные параметры
            'SБЭТ, м²/г', 'а₀, ммоль/г', 'E, кДж/моль', 'Ws, см³/г', 'Sme, м²/г',
            # Расчетные параметры
            'W₀, см³/г (расч.)', 'E₀, кДж/моль (расч.)', 'x₀, нм (расч.)', 'Wme, см³/г (расч.)',
            # Предсказанные параметры
            'Металл (предсказано)', 'Лиганд (предсказано)', 'Растворитель (предсказано)',
            'm (соли), г (предсказано)', 'm(кис-ты), г (предсказано)', 'Vсин. (р-ля), мл (предсказано)',
            'Т.син., °С (предсказано)', 'Т суш., °С (предсказано)', 'Tрег, ᵒС (предсказано)'
        ],
        'Значение': [
            # Входные значения
            input_params.get('SBAT_m2_gr'), input_params.get('a0_mmoll_gr'), input_params.get('E_kDg_moll'),
            input_params.get('Ws_cm3_gr'), input_params.get('Sme_m2_gr'),
            # Расчетные значения
            derived_params.get('W0_cm3_g') or prediction_results.get('derived_features', {}).get('W0_cm3_g'),
            derived_params.get('E0_KDG_moll') or prediction_results.get('derived_features', {}).get('E0_KDG_moll'),
            derived_params.get('x0_nm') or prediction_results.get('derived_features', {}).get('x0_nm'),
            derived_params.get('Wme_cm3_gr') or prediction_results.get('derived_features', {}).get('Wme_cm3_gr'),
            # Предсказанные значения
            prediction_results.get('metal', {}).get('metal_type'),
            prediction_results.get('ligand', {}).get('ligand_type'),
            prediction_results.get('solvent', {}).get('solvent_type'),
            prediction_results.get('salt_mass'),
            prediction_results.get('acid_mass'),
            prediction_results.get('synthesis_volume'),
            prediction_results.get('tsyn', {}).get('temperature'),
            prediction_results.get('tdry', {}).get('temperature'),
            prediction_results.get('treg', {}).get('temperature')
        ],
        'Уверенность (%)': [
            # Для входных и расчетных параметров нет уверенности
            None, None, None, None, None, None, None, None, None,
            # Уверенность для предсказанных параметров
            prediction_results.get('metal', {}).get('confidence', 0) * 100 if prediction_results.get('metal', {}).get('confidence') is not None else None,
            prediction_results.get('ligand', {}).get('confidence', 0) * 100 if prediction_results.get('ligand', {}).get('confidence') is not None else None,
            prediction_results.get('solvent', {}).get('confidence', 0) * 100 if prediction_results.get('solvent', {}).get('confidence') is not None else None,
            None, None, None,  # Для регрессионных моделей нет уверенности
            prediction_results.get('tsyn', {}).get('confidence', 0) * 100 if prediction_results.get('tsyn', {}).get('confidence') is not None else None,
            prediction_results.get('tdry', {}).get('confidence', 0) * 100 if prediction_results.get('tdry', {}).get('confidence') is not None else None,
            prediction_results.get('treg', {}).get('confidence', 0) * 100 if prediction_results.get('treg', {}).get('confidence') is not None else None,
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Форматирование данных
    df['Уверенность (%)'] = df['Уверенность (%)'].apply(
        lambda x: f"{x:.1f}" if pd.notna(x) else "-"
    )
    
    # Форматируем числовые значения с учетом их типа
    df['Значение'] = df['Значение'].apply(
        lambda x: f"{x:.3f}" if isinstance(x, (int, float)) else x
    )
    
    return df

def create_download_button(download_data: pd.DataFrame) -> None:
    """
    Создает кнопку для скачивания результатов.
    
    Args:
        download_data: DataFrame с данными для скачивания
    """
    # Преобразуем DataFrame в Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        download_data.to_excel(writer, index=False, sheet_name="MOF Синтез")
    buffer.seek(0)
    
    # Кнопка скачивания
    st.subheader("Сохранение результатов")
    st.write("Вы можете скачать полный отчет с входными параметрами и результатами предсказаний.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="💾 Скачать рецепт синтеза (Excel)",
            data=buffer,
            file_name="MOF_методика_синтеза.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# --- Основная функция страницы ---

def show() -> None:
    """Главная функция отображения страницы предсказания MOF-синтеза."""
    # Загружаем базовые стили и минимальные стили для улучшения интерфейса
    load_theme_css()
    inject_minimal_css()
    
    # Настройка страницы
    st.title("AI-синтез металлорганических каркасов")
    st.write("Система использует машинное обучение для предсказания оптимальных параметров синтеза металлорганических каркасов с заданными свойствами")
    
    # Сохраняем состояние между запусками в сессию
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    
    if "prediction_results" not in st.session_state:
        st.session_state.prediction_results = None
    
    if "formatted_results" not in st.session_state:
        st.session_state.formatted_results = None
    
    if "download_df" not in st.session_state:
        st.session_state.download_df = None
    
    # Сохраняем состояние индикаторов прогресса
    if "progress_container" not in st.session_state:
        st.session_state.progress_container = None
    
    if "status_text" not in st.session_state:
        st.session_state.status_text = None
    
    if "progress_bar" not in st.session_state:
        st.session_state.progress_bar = None
    
    # Отображаем индикатор прогресса
    render_step_indicator(current_step=st.session_state.current_step)
    
    # ЭТАП 1 – Ввод данных
    if st.session_state.current_step == 0:
        # Очистка предыдущих индикаторов, если они остались
        if st.session_state.progress_bar:
            st.session_state.progress_bar.empty()
            st.session_state.progress_bar = None
        if st.session_state.status_text:
            st.session_state.status_text.empty()
            st.session_state.status_text = None
            
        submitted, user_inputs, derived_params = render_input_form()
        
        # Если нажата кнопка отправки, переходим к этапу 2
        if submitted:
            st.session_state.user_inputs = user_inputs
            st.session_state.derived_params = derived_params
            st.session_state.current_step = 1
            # Перезагружаем страницу для обновления состояния
            st.rerun()
    
    # ЭТАП 2 – Запуск ML-конвейера
    elif st.session_state.current_step == 1:
        # Показываем прогресс анализа
        st.subheader("Анализ данных и расчет параметров")
        
        ## Явно очищаем предыдущие состояния, если они существуют
        if "progress_bar" in st.session_state:
            del st.session_state.progress_bar
        if "status_text" in st.session_state:
            del st.session_state.status_text
        
        # Создаем контейнер для индикаторов прогресса
        status_text = st.empty()  # Пустой элемент для текущего статуса
        progress_bar = st.progress(0)  # Прогресс-бар без текста
        
         # Сохраняем ссылки на элементы в сессии
        st.session_state.status_text = status_text
        st.session_state.progress_bar = progress_bar
        
        # Последовательно показываем прогресс анализа
        steps = [
            "Предобработка данных", 
            "Анализ характеристик", 
            "Подбор компонентов", 
            "Расчет пропорций", 
            "Оптимизация температур", 
            "Финализация"
        ]
        
        for i, step in enumerate(steps):
            # Обновляем статус и прогресс отдельно
            status_text.write(f"⚙️ {step}... ({int((i+1) / len(steps) * 100)}%)")
            progress_value = min(100, int((i+1) / len(steps) * 100))
            progress_bar.progress(progress_value)  # Без параметра text
            
            # Имитируем задержку для наглядности прогресса
            time.sleep(0.4)
        
        # Получаем предсказания от модели - добавляем обработку ошибок
        try:
            predictor: PredictorService = st.session_state.get("_predictor") or PredictorService()
            st.session_state._predictor = predictor
            
            # Проверяем, что user_inputs существует
            if not hasattr(st.session_state, 'user_inputs') or not st.session_state.user_inputs:
                raise ValueError("Отсутствуют введенные параметры. Пожалуйста, вернитесь на шаг ввода данных.")
            
            # Вызываем run_full_prediction только с допустимыми аргументами
            results = predictor.run_full_prediction(**st.session_state.user_inputs)
            
            # Проверяем, что результаты не пустые
            if not results:
                raise ValueError("Модель вернула пустые результаты.")
                
            st.session_state.prediction_results = results
            
            # Форматируем результаты
            cards_data = format_prediction_results_for_display(results)
            st.session_state.formatted_results = cards_data
            
            # Создаем DataFrame для скачивания
            download_df = prepare_download_df(
                st.session_state.user_inputs, 
                results, 
                st.session_state.derived_params
            )
            st.session_state.download_df = download_df
            
            # Завершаем индикацию загрузки
            progress_bar.progress(100)  # Без параметра text
            status_text.write("✅ Анализ завершен!")
            
            # Показываем сообщение об успехе
            st.success("✅ Оптимальные параметры синтеза успешно рассчитаны")
            
            # Автоматически переходим к следующему шагу через 2 секунды
            time.sleep(2)
            st.session_state.current_step = 2
            st.rerun()
            
        except Exception as e:
            # В случае ошибки показываем сообщение и возвращаемся к началу
            if st.session_state.progress_bar:
                st.session_state.progress_bar.empty()
            if st.session_state.status_text:
                st.session_state.status_text.empty()
                
            st.error(f"Произошла ошибка при расчете параметров: {str(e)}")
            st.warning("Пожалуйста, попробуйте другие входные значения.")
            
            # Добавляем кнопку для возврата к началу
            if st.button("⬅️ Вернуться к вводу данных"):
                st.session_state.current_step = 0
                st.session_state.progress_bar = None
                st.session_state.status_text = None
                st.rerun()
    
    # ЭТАП 3 – Отображение результатов
    elif st.session_state.current_step == 2:
        # Очищаем все индикаторы прогресса, если они существуют
        if st.session_state.progress_bar:
            st.session_state.progress_bar.empty()
            st.session_state.progress_bar = None
        if st.session_state.status_text:
            st.session_state.status_text.empty()
            st.session_state.status_text = None
        
        # Отображаем результаты
        if st.session_state.formatted_results is not None:
            display_predicted_parameters(st.session_state.formatted_results)
            
            # Добавляем кнопку скачивания
            if st.session_state.download_df is not None:
                create_download_button(st.session_state.download_df)
            
            # Добавляем кнопку для возврата к началу
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; margin-top: 2rem;'>", unsafe_allow_html=True)
            if st.button("🔄 Начать новый расчет", use_container_width=False):
                # Сбрасываем состояние и возвращаемся к началу
                st.session_state.current_step = 0
                st.session_state.prediction_results = None
                st.session_state.formatted_results = None
                st.session_state.download_df = None
                st.session_state.progress_bar = None
                st.session_state.status_text = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Если результаты отсутствуют, показываем ошибку и возвращаемся на шаг 1
            st.error("Произошла ошибка при обработке результатов. Пожалуйста, повторите ввод данных.")
            if st.button("⬅️ Вернуться к вводу данных"):
                st.session_state.current_step = 0
                st.session_state.progress_bar = None
                st.session_state.status_text = None
                st.rerun()


if __name__ == "__main__":
    show()